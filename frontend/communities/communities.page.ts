import { Observable, Subscription } from 'rxjs';
import { map } from 'rxjs/operators';
import { ChangeDetectorRef, Component, OnInit, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router';
import { ModalController } from '@ionic/angular';
import { CreateCommunityPopupComponent } from 'src/app/components/create-community-popup/create-community-popup.component';
import { Community, CommunityService } from 'src/app/services/community.service';


@Component({
  selector: 'app-communities',
  templateUrl: './communities.page.html',
  styleUrls: ['./communities.page.scss'],
})
export class CommunitiesPage implements OnInit {
  communities: Community[] = [];
  myCommunities: Community[] = [];
  newCommunities: Community[] = [];
  private subscription: Subscription;
  

  constructor
  (
    private router: Router,
    private modalController: ModalController,
    private communityService: CommunityService,
    private cdr: ChangeDetectorRef
  ) { 
    this.loadCommunities(); 
    this.loadMyCommunities();
  }

  ngOnInit() {
  }
  

  openCommunity(communityId) {
    this.router.navigate(['tabs/feed/communities/community', communityId]);
  }

  openCommunitiesOverview() {
    this.router.navigate(['tabs/feed/communities/overview']);
  }

  async openCommunityPopup() {
    const modal = await this.modalController.create({
      component: CreateCommunityPopupComponent,
      cssClass: 'modal-transparent-background',
      backdropDismiss: true
    });
       
    modal.onDidDismiss().then((dataReturned) => {
      if (dataReturned.data?.result === 'continue') {
        this.router.navigate(['tabs/feed/communities/communities-creation']);
      }
    });
    await modal.present(); 
  }

  private async loadCommunities() {
    (await this.communityService.getAllCommunities()).subscribe(communities => {
      this.communities = communities;
      console.log('Loaded communities:', this.communities);
    }, error => {
      console.error('Error loading communities:', error);
    });
  }

  
  private async loadMyCommunities() {
    (await this.communityService.getCurrentUserCommunities()).subscribe(communities => {
      this.myCommunities = communities;
      console.log('My communities:', this.myCommunities);
    }, error => {
      console.error('Error loading communities:', error);
    });
  }
  

  
  
  

  
  
}
