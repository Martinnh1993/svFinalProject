import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { NewCommunitiesPage } from './new-communities.page';

const routes: Routes = [
  {
    path: '',
    component: NewCommunitiesPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class NewCommunitiesPageRoutingModule {}
