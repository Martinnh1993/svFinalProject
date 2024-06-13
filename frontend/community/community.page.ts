import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Community, CommunityPost, CommunityService, CommunityUser } from 'src/app/services/community.service';
import { Observable, Subscription, BehaviorSubject  } from 'rxjs';
import { BucketFireStorageService } from 'src/app/services/bucket-fire-storage.service';
import { Profile, ProfileService } from 'src/app/services/profile.service';
import { NgForm } from '@angular/forms';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { AlertController } from '@ionic/angular';

@Component({
  selector: 'app-community',
  templateUrl: './community.page.html',
  styleUrls: ['./community.page.scss'],
})
export class CommunityPage implements OnInit {
  private subscription: Subscription;
  community: Community | null = null;
  communityPosts: CommunityPost[] = [];
  communityUsers: CommunityUser[] = [];
  communityRequests: CommunityUser[] = [];
  cachedImageUrls: { [index: number]: string } = {};
  id;
  activeTab: string = 'feed';
  myProfilePicUrl;
  myProfilePic;
  myRole: number;
  newPost = {
    description: '',
    image: null as File | null
  };

  constructor(
    private route: ActivatedRoute,
    private communityService: CommunityService,
    private profileService: ProfileService,
    private storageService: BucketFireStorageService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private alertController: AlertController
    
  ) {
    this.id =+ this.route.snapshot.paramMap.get('id');
    this.loadCommunities();
    this.loadCommunityPosts();
    this.loadCommunityUsers();
    this.loadCommunityRequests();
  }

  ngOnInit(){
    
    
    this.getProfilePic();
    
  }

  private getProfilePic() {
    this.profileService
      .getProfile()
      .then((response: Observable<any>) => {
        response.subscribe({
          next: async (profile: Profile) => {
            this.myProfilePic = profile.profilePic;
            this.myProfilePicUrl = await this.storageService.getBucketUrl(this.myProfilePic);

            // Loop through existing communityUsers to find matching username
            for (let user of this.communityUsers) {
              if (user.username === profile.username) {
                this.myRole = user.role;
                break;
              }
            }
          },
          error: (err) => {
            console.error('Error fetching profile:', err);
          }
        });
      })
      .catch((error) => {
        console.error('Error in getProfile promise:', error);
      });
  }

  private async loadCommunities() {
    (await this.communityService.getCommunityById(this.id)).subscribe({
      next: (community) => {
        this.community = community;
        console.log('in community:', this.community);
        
      },
      error: (error) => console.error('Error fetching community:', error)
    });
  }

  private async loadCommunityPosts() {
    (await this.communityService.getCommunityPosts(this.id)).subscribe({
      next: (communityPost) => {
        this.communityPosts = communityPost;
        
        this.preloadPostUserImageUrls().then(() => {
          console.log('Community post Users after preloading images:', this.communityPosts);
        });
      },
      error: (error) => console.error('Error fetching community:', error)
    });
  }

  private async loadCommunityUsers() {
    try {
        // Await the Promise returned by the service, then subscribe to the Observable
        const usersObservable = await this.communityService.getCommunityUsers(this.id);
        usersObservable.subscribe({
            next: (users) => {
                // Check if the incoming data is nested and needs flattening
                if (Array.isArray(users) && users.length === 1 && Array.isArray(users[0])) {
                    this.communityUsers = users[0]; // Flatten the array by taking the first element
                } else if (Array.isArray(users)) {
                    this.communityUsers = users; // Use users directly if already flat
                } else {
                    console.error('Unexpected response format:', users);
                }
    
                // Load additional data or perform actions after loading users
                this.preloadUserImageUrls().then(() => {
                    console.log('Community Users after preloading images:', this.communityUsers);
                });
            },
            error: (error) => console.error('Error fetching community users:', error)
        });
    } catch (error) {
        console.error('Failed to fetch community users:', error);
    }
  }

  private async loadCommunityRequests() {
    try {
      const requestObservable = await this.communityService.getCommunityRequests(this.id);
      requestObservable.subscribe({
        next: (users) => {
          if (Array.isArray(users) && users.length === 1 && Array.isArray(users[0])) {
            this.communityRequests = users[0];
          } else if (Array.isArray(users)) {
            this.communityRequests = users;
          } else {
            console.error('Unexpected response format:', users);
          }

          this.preloadRequestImageUrls().then(() => {
            console.log('Community requests after preloading images:', this.communityRequests);
            this.cdr.detectChanges(); // Manually trigger change detection
          });
        },
        error: (error) => console.error('Error fetching community users:', error)
      });
    } catch (error) {
      console.error('Failed to fetch community users:', error);
    }
  }

  async preloadRequestImageUrls() {
    for (let i = 0; i < this.communityRequests.length; i++) {
      if (!this.communityRequests[i].imageUrl && this.communityRequests[i].profilePic) {
        this.communityRequests[i].imageUrl = await this.getRequestBucketUrl(this.communityRequests[i].profilePic, i);
      }
    }
  }

  async getRequestBucketUrl(imageUrl: string, index: number): Promise<string> {
    try {
      if (this.cachedImageUrls[index]) {
        return this.cachedImageUrls[index];
      } else {
        const imageUrlFromService = await this.storageService.getBucketUrl(imageUrl);
        this.communityRequests[index].imageUrl = imageUrlFromService;
        this.cachedImageUrls[index] = imageUrlFromService;
        return imageUrlFromService;
      }
    } catch (error) {
      console.error('Error fetching image URL:', error);
      return '/path/to/default/image.jpg'; // Default image path if an error occurs
    }
  }


  async preloadUserImageUrls() {
    for (let i = 0; i < this.communityUsers.length; i++) {
      if (!this.communityUsers[i].imageUrl && this.communityUsers[i].profilePic) {
        this.communityUsers[i].imageUrl = await this.getUserBucketUrl(this.communityUsers[i].profilePic, i);
      }
    }
  }

  async getUserBucketUrl(imageUrl: string, index: number): Promise<string> {
    try {
      if (this.cachedImageUrls[index]) {
        return this.cachedImageUrls[index];
      } else {
        const imageUrlFromService = await this.storageService.getBucketUrl(imageUrl);
        this.communityUsers[index].imageUrl = imageUrlFromService;
        this.cachedImageUrls[index] = imageUrlFromService;
        return imageUrlFromService;
      }
    } catch (error) {
      console.error('Error fetching image URL:', error);
      return '/path/to/default/image.jpg'; // Default image path if an error occurs
    }
  }

  async preloadPostUserImageUrls() {
    for (let i = 0; i < this.communityPosts.length; i++) {
      if (!this.communityPosts[i].user.imageUrl && this.communityPosts[i].user.profilePicturePath) {
        this.communityPosts[i].user.imageUrl = await this.getUserBucketUrl(this.communityPosts[i].user.profilePicturePath, i);
      }
    }
  }

  async getPostUserBucketUrl(imageUrl: string, index: number): Promise<string> {
    try {
      if (this.cachedImageUrls[index]) {
        return this.cachedImageUrls[index];
      } else {
        const imageUrlFromService = await this.storageService.getBucketUrl(imageUrl);
        this.communityPosts[index].user.imageUrl = imageUrlFromService;
        this.cachedImageUrls[index] = imageUrlFromService;
        return imageUrlFromService;
      }
    } catch (error) {
      console.error('Error fetching image URL:', error);
      return '/path/to/default/image.jpg'; // Default image path if an error occurs
    }
  }
  
  openMembersPage() {
    this.router.navigate(['tabs/feed/communities/community', this.id, 'members'], {
      queryParams: { communityName: this.community.name }
    });
  }
  
  openOptions() {
    this.router.navigate(['tabs/feed/communities/community', this.id, 'settings'], {
      queryParams: { communityName: this.community.name, myRole: this.myRole }
    })
  }

    async confirm(user) {
      try {
        const response = await this.communityService.acceptRequestCommunity(this.id, user.userId);
        console.log('Accept response:', response);
        if (response.success) {
          this.communityUsers.push(user);
          this.removeUserFromRequests(user.userId);
        }
      } catch (error) {
        console.error('Error confirming request:', error);
      }
    }
    
  
    async deny(user) {
      try {
        const response = await this.communityService.denyRequestCommunity(this.id, user.userId);
        console.log('Deny response:', response);
        if (response.success) {
          this.removeUserFromRequests(user.userId);
        }
      } catch (error) {
        console.error('Error confirming request:', error);
      }
    }

    private removeUserFromRequests(userId) {
      this.communityRequests = this.communityRequests.filter(user => user.userId !== userId);
      console.log('Updated community requests:', this.communityRequests);
      this.cdr.detectChanges(); // Manually trigger change detection
    }

    getTimeSince(dateStr: string): string {
      const now = new Date();
      const postDate = new Date(dateStr);
      const diff = now.getTime() - postDate.getTime();
  
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / (3600000 * 24));
  
      if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
      } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      } else {
        return 'Just now';
      }
    }

    async submitPost() {
      if (this.validateFormData()) {
        const formData = new FormData();
        formData.append('description', this.newPost.description);
        if (this.newPost.image) {
          formData.append('image_path', this.newPost.image, this.newPost.image.name);
        }
  
        try {
          const response = await this.communityService.createCommunityPost(formData, this.id);
          console.log('Post created:', response);
          this.loadCommunityPosts();
        } catch (error) {
          console.error('Error submitting post:', error);
        }
      } else {
        console.log('Form data is invalid');
      }
    }
  
    validateFormData(): boolean {
      return this.newPost.description.trim() !== '' || this.newPost.image != null;
    }


    async openGalleryForPost() {
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
    
        // Fetch the image as a blob from its webPath
        const response = await fetch(image.webPath);
        const blob = await response.blob();
        
        // Store the image as a File object in your component's state
        this.newPost.image = new File([blob], `post_image.${image.format}`, { type: blob.type });
    
      } catch (error) {
        console.error('Error selecting image:', error);
        // Assuming showAlert is a method in the same component or a utility service
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
}
