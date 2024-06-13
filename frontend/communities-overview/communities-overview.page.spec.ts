import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommunitiesOverviewPage } from './communities-overview.page';

describe('CommunitiesOverviewPage', () => {
  let component: CommunitiesOverviewPage;
  let fixture: ComponentFixture<CommunitiesOverviewPage>;

  beforeEach(async(() => {
    fixture = TestBed.createComponent(CommunitiesOverviewPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
