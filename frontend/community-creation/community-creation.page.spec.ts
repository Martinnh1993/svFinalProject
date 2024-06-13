import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommunityCreationPage } from './community-creation.page';

describe('CommunityCreationPage', () => {
  let component: CommunityCreationPage;
  let fixture: ComponentFixture<CommunityCreationPage>;

  beforeEach(async(() => {
    fixture = TestBed.createComponent(CommunityCreationPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
