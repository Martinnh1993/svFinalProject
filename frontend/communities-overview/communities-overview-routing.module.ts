import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { CommunitiesOverviewPage } from './communities-overview.page';

const routes: Routes = [
  {
    path: '',
    component: CommunitiesOverviewPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class CommunitiesOverviewPageRoutingModule {}
