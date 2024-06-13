import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { CommunityInvitePage } from './community-invite.page';

const routes: Routes = [
  {
    path: '',
    component: CommunityInvitePage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class CommunityInvitePageRoutingModule {}
