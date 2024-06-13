import { Component, Input, OnInit } from '@angular/core';
import { BucketFireStorageService } from 'src/app/services/bucket-fire-storage.service';
import { Friend, FriendsService } from 'src/app/services/friends.service';
import { Observable } from 'rxjs';
import { ModalController } from '@ionic/angular';
import { ActivatedRoute } from '@angular/router';
import { Profile, ProfileService } from 'src/app/services/profile.service';
import { CommunityService } from 'src/app/services/community.service';

@Component({
  selector: 'app-community-invite',
  templateUrl: './community-invite.page.html',
  styleUrls: ['./community-invite.page.scss'],
})
export class CommunityInvitePage implements OnInit {
  @Input() communityName: string;
  @Input() communityId;
  selectedFriends: string[] = [];
  friendsData: Friend[] = [];
  filteredFriendsData = [...this.friendsData];
  cachedImageUrlsAllFriends: { [index: number]: string } = {};
  userData: Profile = {} as Profile;
  user_id: string;
  searchTerm: any;

  constructor(
    private friendService: FriendsService,
    private storageService: BucketFireStorageService,
    private profileService: ProfileService,
    private communityService: CommunityService,
    private modalController: ModalController,
    private route: ActivatedRoute

  ) { }

  ngOnInit() {
    this.fillFriend()
  }

  private fillFriend() {
    this.friendService.getFriends().then((response: Observable<any>) => {
      response.subscribe({
        next: (friendData: Friend[]) => {
          console.log('friendData:', friendData);
          
          this.friendsData = friendData;
          this.filteredFriendsData = friendData;
          this.preloadFriendImages();

          console.log('friendData', this.filteredFriendsData);
        }
      });
    }).catch((error: any) => {
      // Handle the error condition
      throw error;
    });
  }

  async preloadFriendImages() {
    for (let i = 0; i < this.filteredFriendsData.length; i++) {
      if (!this.filteredFriendsData[i].imageUrl && this.filteredFriendsData[i].profile_pic) {
        this.filteredFriendsData[i].imageUrl = await this.getBucketUrlallFriends(this.filteredFriendsData[i].profile_pic, i);
      }
    }
  }

  async getBucketUrlallFriends(imageUrl: string, index: number) {

    if (this.cachedImageUrlsAllFriends[index]) {
      this.filteredFriendsData[index].imageUrl = this.cachedImageUrlsAllFriends[index]
      return this.cachedImageUrlsAllFriends[index];
    } else {
      const imageUrlFromService = await this.storageService.getBucketUrl(imageUrl);
      this.filteredFriendsData[index].imageUrl = imageUrlFromService
      this.cachedImageUrlsAllFriends[index] = imageUrlFromService;
      return imageUrlFromService;
    }
  }

  closeModal() {
    this.modalController.dismiss();
  }

  customPopoverOptions = {
    header: 'Friend',
    subHeader: 'Select a friend you would like to invite to the community',
    message: 'You can only invite one friend at a time',
  };

  private async getId(username): Promise<string> {
    try {
      const response = await (await this.profileService.getPublicProfile(username)).toPromise();
      return response.id;
    } catch (error) {
      throw error;
    }
  }
  
  async inviteToCommunity(friend) {
    try {
      let id = await this.getId(friend);
      console.log('id:', id);
      
      const response = await this.communityService.InviteToCommunity(this.communityId, id);
      if (response.success) {
        console.log(response.message);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  }

  searchFriend(event: any): void {
    const searchTerm = event.detail.value.toLowerCase();  // Accessing the input value

    if (!searchTerm) {
      this.filteredFriendsData = this.friendsData; // Reset to all friends if search term is cleared
      return;
    }

    this.filteredFriendsData = this.friendsData.filter((friend) =>
      friend.username.toLowerCase().includes(searchTerm)
    );
  }  
}


