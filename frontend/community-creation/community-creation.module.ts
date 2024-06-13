import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { CommunityCreationPageRoutingModule } from './community-creation-routing.module';

import { CommunityCreationPage } from './community-creation.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    CommunityCreationPageRoutingModule
  ],
  declarations: [CommunityCreationPage]
})
export class CommunityCreationPageModule {}
