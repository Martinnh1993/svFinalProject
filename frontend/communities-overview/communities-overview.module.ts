import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { CommunitiesOverviewPageRoutingModule } from './communities-overview-routing.module';

import { CommunitiesOverviewPage } from './communities-overview.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    CommunitiesOverviewPageRoutingModule
  ],
  declarations: [CommunitiesOverviewPage]
})
export class CommunitiesOverviewPageModule {}
