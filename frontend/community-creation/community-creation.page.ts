import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AlertController, ModalController } from '@ionic/angular';
import { LocationPage } from '../location/location.page';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { PhotoService } from 'src/app/services/photo.service';
import { CommunityService } from 'src/app/services/community.service';
import { NgForm } from '@angular/forms';

interface Community {
  banner;
  name,
  image,
  about,
  location: Location,
  closed,
  invite
}

interface Location {
  street,
  city,
  country,
  timezone,
  latitude,
  longitude
}

@Component({
  selector: 'app-community-creation',
  templateUrl: './community-creation.page.html',
  styleUrls: ['./community-creation.page.scss'],
})
export class CommunityCreationPage implements OnInit{
  selectedLogoFile: File | null = null;
  selectedBannerFile: File | null = null;
  community: Community | null = null;
  id: number;

  constructor
  (
    private modalConteroller: ModalController,
    private alertController: AlertController,
    private router: Router,
    private photoService: PhotoService,
    private communityService: CommunityService,
    private route: ActivatedRoute,
  ) 
  {   
    this.community = {
      name: '',
      about: '',
      location: {
        street: '',
        city: '',
        country: '',
        timezone: '',
        latitude: '',
        longitude: ''
      },
      closed: false,
      invite: false,
      image: null,
      banner: null,
    };
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.id = params['communityId'];
    });
    if (this.id != null) {
      this.loadCommunity();
    }
  }

  private async loadCommunity() {
    (await this.communityService.getCommunityById(this.id)).subscribe({
      next: (community) => {
        this.mapCommunityData(community);
        console.log('in community:', this.community);
      },
      error: (error) => console.error('Error fetching community:', error)
    });
  }

  private mapCommunityData(community: any) {
    this.community.name = community.name;
    this.community.about = community.description; // Adjust if your property names differ
    this.community.location.street = community.location.street;
    this.community.location.city = community.location.city;
    this.community.location.country = community.location.country;
    this.community.location.timezone = community.location.timezone;
    this.community.location.latitude = community.location.latitude;
    this.community.location.longitude = community.location.longitude;
    this.community.closed = community.is_private;
    this.community.invite = community.is_closed;
    this.community.image = community.imagePath; // Ensure these property names match those sent by your server
    this.community.banner = community.bannerPath;
  } 

  async openLocation() {
    const modal = await this.modalConteroller.create({
      component: LocationPage,
    });
  
    await modal.present();
  
    // Handling the data when the modal is dismissed
    const { data } = await modal.onDidDismiss();
    
    if (data) {
      console.log('Returned data:',data)
      this.community.location = {
        street: data.street || '',
        city: data.city || '',
        country: data.country || '',
        timezone: data.timezone || 'Default timezone',
        longitude: data.longitude || 0,
        latitude: data.latitude || 0,
      };
      console.log('Updated community location:', this.community.location);
    } else {
      console.log('No data returned from location modal, or missing expected fields');
    }
  }

  get formattedLocation(): string {
    const { street, city, country } = this.community.location;
    // Create an array, filter out empty strings, and join with commas
    return [street, city, country].filter(part => part).join(', ');
  }

  async openGallery(imageType) {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        source: CameraSource.Photos,
        correctOrientation: true,
        resultType: CameraResultType.Uri
      });
  
      const validFormats = ['jpeg', 'jpg', 'png', 'gif'];
      if (!image.format || !validFormats.includes(image.format.toLowerCase())) {
        throw new Error('Unsupported file type');
      }
  
      if (imageType === 'logo') {
        this.community.image = image.webPath;
      } else if (imageType === 'banner') {
        this.community.banner = image.webPath;
      }
  
      const response = await fetch(image.webPath);
      const blob = await response.blob();
      if (imageType === 'logo') {
        this.selectedLogoFile = new File([blob], 'community_logo.' + image.format, { type: blob.type });
      } else if (imageType === 'banner') {
        this.selectedBannerFile = new File([blob], 'community_banner.' + image.format, { type: blob.type });
      }
    } catch (error) {
      console.error('Error selecting image:', error);
      await this.showAlert('Invalid Selection', 'Please select a valid image file (JPEG, PNG, GIF).');
    }
  }
  

  async showAlert(header: string, message: string) {
    const alert = await this.alertController.create({
      header: header,
      message: message,
      buttons: ['OK']
    });

    await alert.present();
  }

  async createOrUpdateCommunity(form: NgForm) {
    if (form.valid) {
      const formData = new FormData();
      formData.append('name', this.community.name);
      formData.append('description', this.community.about);
      formData.append('street', this.community.location.street || '');
      formData.append('city', this.community.location.city || '');
      formData.append('country', this.community.location.country || '');
      formData.append('timezone', this.community.location.timezone || '');
      formData.append('longitude', this.community.location.longitude || '');
      formData.append('latitude', this.community.location.latitude || '');
      formData.append('is_private', this.community.closed);
      formData.append('is_closed', this.community.invite);
      if (this.selectedLogoFile) {
        formData.append('image_path', this.selectedLogoFile, this.selectedLogoFile.name);
      }
      if (this.selectedBannerFile) {
        formData.append('banner_path', this.selectedBannerFile, this.selectedBannerFile.name);
      }

      if (!this.id) {
        this.createCommunity(formData);
      } else {
        this.updateCommunity(this.id, formData)
      }
    } else {
      console.error('Form is invalid');
      await this.showAlert('Invalid Form', 'Please fill in all required fields.');
    }
  }

  async createCommunity(form) {
      try {
        const response = await this.communityService.createCommunity(form);
        console.log('Community created successfully:', response);
        await this.showAlert('Success', 'Community created successfully.');
        this.router.navigate(['/tabs/feed/communities']); // Update with your actual route
      } catch (error) {
        console.error('Error creating community:', error);
        await this.showAlert('Error', 'There was an error creating the community. Please try again.');
      }
    }

    async updateCommunity(id, form) {
      try {
        const response = await this.communityService.updateCommunity(id,form);
        console.log('Community updated successfully:', response);
        await this.showAlert('Success', 'Community updated successfully.');
        this.router.navigate(['/tabs/feed/communities']); // Update with your actual route
      } catch (error) {
        console.error('Error creating community:', error);
        await this.showAlert('Error', 'There was an error creating the community. Please try again.');
      }
    }   

  
    
}
