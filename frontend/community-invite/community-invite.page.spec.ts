import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommunityInvitePage } from './community-invite.page';

describe('CommunityInvitePage', () => {
  let component: CommunityInvitePage;
  let fixture: ComponentFixture<CommunityInvitePage>;

  beforeEach(async(() => {
    fixture = TestBed.createComponent(CommunityInvitePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
