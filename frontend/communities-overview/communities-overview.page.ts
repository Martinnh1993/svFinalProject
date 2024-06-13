import { Component, OnDestroy, OnInit } from '@angular/core';
import { Community, CommunityService } from 'src/app/services/community.service';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';
import { ModalController } from '@ionic/angular';
import { JoinOpenCommunityComponent } from 'src/app/components/join-open-community/join-open-community.component';
import { JoinClosedCommunityComponent } from 'src/app/components/join-closed-community/join-closed-community.component';

@Component({
  selector: 'app-communities-overview',
  templateUrl: './communities-overview.page.html',
  styleUrls: ['./communities-overview.page.scss'],
})
export class CommunitiesOverviewPage implements OnInit, OnDestroy {
  private subscriptions: Subscription = new Subscription();
  communities: Community[] = [];
  allCommunities: Community[] = [];
  searchTerm: string = '';

  constructor(
    
    private communityService: CommunityService,
    private router: Router,
    private modalController: ModalController
    
  ) { 
    this.loadCommunities(); 
  }

  ngOnInit() {
  }
  

  async openJoinPopup(communityId) {
    console.log("open joined community clicked")
    const modal = await this.modalController.create({
      component: JoinOpenCommunityComponent,
      cssClass: 'modal-transparent-background',
      backdropDismiss: true
    });

    modal.onDidDismiss().then((dataReturned) => {
      console.log(dataReturned)
      if (dataReturned.data?.result === 'join') {
        this.communityService.joinOpenCommunity(communityId)
      }
    });
    await modal.present(); 
  }

  async openRequestPopup(communityId) {
    const modal = await this.modalController.create({
      component: JoinClosedCommunityComponent,
      cssClass: 'modal-transparent-background',
      backdropDismiss: true
    });

    modal.onDidDismiss().then((dataReturned) => {
      if (dataReturned.data?.result === 'request') {
        console.log('inside if')
        const response = this.communityService.requestCommunity(communityId)
        console.log('response:', response);
        
      }
    });
    await modal.present(); 
  }

  private async loadCommunities() {
    (await this.communityService.getAllCommunities()).subscribe(communities => {
      this.communities = communities;
      this.allCommunities = [...communities];
      console.log('Loaded communities:', this.communities);
    }, error => {
      console.error('Error loading communities:', error);
    });
  }
  
  searchCommunities() {
    if (this.searchTerm.trim() !== '') {
        const lowerCaseSearchTerm = this.searchTerm.toLowerCase();
        this.communities = this.allCommunities.filter(
            community => community.name.toLowerCase().includes(lowerCaseSearchTerm)
        );
    } else {
        // Show all communities when there is no search term
        this.communities = [...this.allCommunities];
    }
  }

  openOptions() {
    throw new Error('Method not implemented.');
    }

  ngOnDestroy() {
    this.subscriptions.unsubscribe();
  }
}

