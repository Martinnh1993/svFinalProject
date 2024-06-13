import { HttpClient } from '@angular/common/http';
import { AfterViewChecked, AfterViewInit, Component, ElementRef, NgZone, OnInit, Renderer2, ViewChild } from '@angular/core';
import { Validators } from '@angular/forms';
import { Geolocation, Position, PositionOptions } from '@capacitor/geolocation';
import { environment } from 'src/environments/environment';
import { BehaviorSubject, Subscription } from 'rxjs';
import { LoadingController, ModalController } from '@ionic/angular';

interface Location {
  street;
  city;
  country;
  timezone;
  longitude;
  latitude;
  distance;
}

declare var google;

@Component({
  selector: 'app-location',
  templateUrl: './location.page.html',
  styleUrls: ['./location.page.scss'],
})
export class LocationPage implements OnInit   {
  currentLocation: Location;
  selectedLocation: Location;
  placesLibrary;
  postDescriptionForm: any;
  formBuilder: any;
  
  placesService: any;
  places: any[] = [];
  placeUrl;
  
  
  constructor
  (
    private http: HttpClient,
    private modalCtrl: ModalController,
    public loadingController: LoadingController
  ) 
  {
    this.getCurrentPosition();
  }


  ngOnInit() {
    console.log('Initializing Google Maps API');
    this.loadGoogleMapsApi();
  }

  loadGoogleMapsApi() {
    if ((window as any).google) {
      console.log('Google Maps API already loaded');
      this.initPlacesService();
    } else {
      console.log('Loading Google Maps API');
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${environment.googleMapsApi}&libraries=places`;
      document.head.appendChild(script);
      script.onload = () => {
        console.log('Google Maps API script loaded');
        this.initPlacesService();
      };
      script.onerror = () => {
        console.error('Error loading Google Maps API script');
      };
    }
  }

  initPlacesService() {
    if ((window as any).google) {
      this.placesService = new google.maps.places.AutocompleteService();
      console.log('Places service initialized');
    } else {
      console.error('Google Maps API is not available.');
    }
  }

  async getCurrentPosition() {
    try {
      const options: PositionOptions = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      };

      const position: Position = await Geolocation.getCurrentPosition(options);

      const { latitude, longitude } = position.coords;

      this.reverseGeocode(latitude, longitude);
    } catch (error) {
      console.error('Error getting current position:', error);
    }
  }

  reverseGeocode(lat: number, lng: number) {
    const url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${environment.googleMapsApi}`;
    this.http.get(url).subscribe(response => {
      if (response['status'] === 'OK') {
        const results = response['results'][0];
        const addressComponents = results['address_components'];
        this.currentLocation = {
          street: this.getAddressComponent(addressComponents, 'route') + ' ' + this.getAddressComponent(addressComponents, 'street_number'),
          city: this.getAddressComponent(addressComponents, 'locality'),
          country: this.getAddressComponent(addressComponents, 'country'),
          longitude: lng,
          latitude: lat,
          timezone: 'Unknown',
          distance: null
        };
        this.selectedLocation = this.currentLocation;
        console.log('Formatted Address:', this.currentLocation);
      } else {
        console.log('Geocoding failed:', response['status']);
      }
    }, error => {
      console.error('Failed to reverse geocode the location:', error);
    });
  }

  getAddressComponent(components, type) {
    const component = components.find(c => c.types.includes(type));
    return component ? component.long_name : '';
  }

  async onSearchChange(event) {
    const query = event.detail.value;
    console.log('Handling search change:', query);
    if (!query.trim().length) {
      console.log('Query is empty after trimming, returning');
      return;
    }
  
    const loading = await this.loadingController.create({
      message: 'Searching...',
    });
    await loading.present();
    console.log('Loading dialog presented');
  
    this.placesService.getPlacePredictions({ input: query }, (predictions, status) => {
      console.log('Received predictions:', predictions);
      if (status !== 'OK') {
        console.error('Error getting predictions:', status);
        this.places = [];
      } else {
        // Parse each prediction and extract needed parts
        this.places = predictions.map(prediction => {
          const terms = prediction.terms;
          return {
            street: terms[0]?.value, 
            city: terms[1]?.value,   
            country: terms[2]?.value,
            fullDescription: prediction.description,
            placeId: prediction.place_id
          };
        });
      }
      loading.dismiss();
      console.log('Loading dialog dismissed', this.places);
    });
  }

  async selectLocation(place) {
    console.log('Selected place from autocomplete:', place);
    if (!place.placeId) {
      console.log('No place_id available, cannot fetch details');
      return;
    }

    this.selectedLocation = {
      street: place.street || '',
      city: place.city || '',
      country: place.country || '',
      timezone: 'Default timezone',
      longitude: 0,
      latitude: 0,
      distance: '0'
    };
  
    try {
      const detailedPlace = await this.fetchPlaceDetails(place.street, place.city, place.country);
      console.log('Fetched detailed place:', detailedPlace);
  
      this.selectedLocation = {
        street: detailedPlace.street || '',
        city: detailedPlace.city || '',
        country: detailedPlace.country || '',
        timezone: detailedPlace.timezone || 'Default timezone',
        longitude: detailedPlace.longitude || 0,
        latitude: detailedPlace.latitude || 0,
        distance: '0'
      };
  
      if (this.currentLocation && detailedPlace.longitude && detailedPlace.latitude) {
        this.selectedLocation.distance = this.calculateDistance(
          this.currentLocation.longitude,
          this.currentLocation.latitude,
          detailedPlace.latitude,
          detailedPlace.longitude
        ).toFixed(2);
      }
    } catch (error) {
      console.error('Error fetching place details:', error);
    }
  }
  
  async fetchPlaceDetails(street, city, country) {
    let level = street ? 'street' : city ? 'city' : 'country';

    switch (level) {
      case 'street':
        this.placeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${street + ',' + city + ',' + country}_ID&key=${environment.googleMapsApi}`;
        break;
      case 'city':
        this.placeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${city + ',' + country}_ID&key=${environment.googleMapsApi}`;
        break;
      case 'country':
        this.placeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${country}_ID&key=${environment.googleMapsApi}`;
     
        break;
    }
    
    try {
      const response = await fetch(this.placeUrl);
      const data = await response.json();
      
      if (data.status !== 'OK') {
        throw new Error('Failed to fetch place details');
      }
      const result = data.results[0];

      return {
        street: this.selectedLocation.street,
        city: this.selectedLocation.city,
        country: this.selectedLocation.country,
        longitude: result.geometry.location.lng,
        latitude: result.geometry.location.lat,
        timezone: 'Default timezone'
      };
    } catch (error) {
      console.error('Error in fetchPlaceDetails:', error);
      throw error; 
    }
  }
  
  extractAddressComponent(result, type) {
    const component = result.address_components.find(c => c.types.includes(type));
    return component ? component.long_name : '';
  }
  
  
  calculateDistance(lon1, lat1, lon2, lat2) {
    const R = 6371; 
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c;
    return distance;
  }
  
  clearPlaces() {
    console.log('Clearing places');
    this.places = [];
  }

  goBackToCurrentLocation() {
    // Set the selectedLocation to the currentLocation
    this.selectedLocation = {
      street: this.currentLocation.street,
      city: this.currentLocation.city,
      country: this.currentLocation.country,
      timezone: this.currentLocation.timezone,
      latitude: this.currentLocation.latitude,
      longitude: this.currentLocation.longitude,
      distance: null    
    };
  }

  close() {
    this.modalCtrl.dismiss()
  }

  select() {
    this.modalCtrl.dismiss({
      'street': this.selectedLocation.street,
      'city': this.selectedLocation.city,
      'country': this.selectedLocation.country,
      'timezone': this.selectedLocation.timezone,
      'latitude': this.selectedLocation.latitude,
      'longitude': this.selectedLocation.longitude
    });
  }
}