import { Observable } from 'rxjs';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IonBackButton, ModalController } from '@ionic/angular';
import { CommunityService } from 'src/app/services/community.service';
import { CommunityInvitePage } from '../community-invite/community-invite.page';
import { Profile, ProfileService } from 'src/app/services/profile.service';
import { CreateCommunityPopupComponent } from 'src/app/components/create-community-popup/create-community-popup.component';

@Component({
  selector: 'app-community-settings',
  templateUrl: './community-settings.page.html',
  styleUrls: ['./community-settings.page.scss'],
})
export class CommunitySettingsPage implements OnInit {
  communityName;
  myRole;
  id;

  constructor(
    private route: ActivatedRoute,
    private communityService: CommunityService,
    private profileService: ProfileService,
    private router: Router,
    private modalController: ModalController
  ) {
    this.id =+ this.route.snapshot.paramMap.get('id');
    this.route.queryParams.subscribe(params => {
      this.myRole = params['myRole']
    });
   }

  ngOnInit() {
    console.log('the is is:', this.id)
    console.log("my role:", this.myRole)
  }

  async openCommunityPopup() {
    const modal = await this.modalController.create({
      component: CreateCommunityPopupComponent,
      cssClass: 'modal-transparent-background',
      backdropDismiss: true
    });
       
    modal.onDidDismiss().then((dataReturned) => {
      if (dataReturned.data?.result === 'continue') {
        this.router.navigate(['tabs/feed/communities/communities-creation'], {
          queryParams: { communityId: this.id}
        })
      }
    });
    await modal.present(); 
  }

  openMembersPage() {
    this.router.navigate(['tabs/feed/communities/community', this.id, 'members'], {
      queryParams: { communityName: this.communityName }
    });
  }

  async openInvitePopup() {
    this.router.navigate(['tabs/feed/communities/community', this.id]);
    
    const modal = await this.modalController.create({
      component: CommunityInvitePage,
      componentProps: {communityName: this.communityName, communityId: this.id},
      cssClass: 'modal-transparent-background',
      backdropDismiss: true
    });

    /* modal.onDidDismiss().then((dataReturned) => {
      if (dataReturned.data?.result === 'join') {
        this.communityService.joinOpenCommunity(communityId)
      }
    }); */
    await modal.present(); 
  }

  public async leaveCommunity() {
    // Confirm dialog asking the user if they really want to leave the community
    const confirmLeave = confirm("Are you sure you want to leave this community?");
    if (!confirmLeave) {
      
      return;  // If user cancels, exit the function without leaving the community
    }
  
    try {
      const response = await this.communityService.leaveCommunity(this.id);
      console.log('Accept response:', response);
      if (response.success) {
        // Navigate away from the current community page upon successful leave
        this.router.navigate(['tabs/feed/communities']);
      }
    } catch (error) {
      console.error('Error confirming request:', error);
    }
  }

  async deleteCommunity() {
    const response = await this.communityService.deleteCommunity(this.id);
    console.log('Accept response:', response)
      if (response.success) {
        // Navigate away from the current community page upon successful leave
        this.router.navigate(['tabs/feed/communities']);
      }
    } catch (error) {
      console.error('Error confirming request:', error);
    }
}
