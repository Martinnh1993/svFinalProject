import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { CommunityCreationPage } from './community-creation.page';

const routes: Routes = [
  {
    path: '',
    component: CommunityCreationPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class CommunityCreationPageRoutingModule {}
