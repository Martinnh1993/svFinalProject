import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { NewCommunitiesPageRoutingModule } from './new-communities-routing.module';

import { NewCommunitiesPage } from './new-communities.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    NewCommunitiesPageRoutingModule
  ],
  declarations: [NewCommunitiesPage]
})
export class NewCommunitiesPageModule {}
