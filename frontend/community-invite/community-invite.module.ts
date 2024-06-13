import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { CommunityInvitePageRoutingModule } from './community-invite-routing.module';

import { CommunityInvitePage } from './community-invite.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    CommunityInvitePageRoutingModule
  ],
  declarations: [CommunityInvitePage]
})
export class CommunityInvitePageModule {}
