import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NewCommunitiesPage } from './new-communities.page';

describe('NewCommunitiesPage', () => {
  let component: NewCommunitiesPage;
  let fixture: ComponentFixture<NewCommunitiesPage>;

  beforeEach(async(() => {
    fixture = TestBed.createComponent(NewCommunitiesPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
