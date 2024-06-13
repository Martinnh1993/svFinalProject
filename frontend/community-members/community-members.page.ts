import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BucketFireStorageService } from 'src/app/services/bucket-fire-storage.service';
import { CommunityService, CommunityUser } from 'src/app/services/community.service';
import { Subscription, Observable } from 'rxjs';
import { Profile, ProfileService } from 'src/app/services/profile.service';
import { ModalController } from '@ionic/angular';
import { OptionMenuComponent } from 'src/app/components/option-menu/option-menu.component';

@Component({
  selector: 'app-community-members',
  templateUrl: './community-members.page.html',
  styleUrls: ['./community-members.page.scss'],
})
export class CommunityMembersPage implements OnInit, OnDestroy {
  private subscriptions: Subscription = new Subscription();
  defaultHref: string;
  communityUsers: CommunityUser[] = [];
  communityUsersAll: CommunityUser[] = [];
  cachedImageUrls: { [index: number]: string } = {};
  groupedCommunityUsers: CommunityUser[][];
  communityName: string;
  id: number;
  myRole: number;
  myUsername;
  searchTerm: any;

  constructor(
    private route: ActivatedRoute,
    private communityService: CommunityService,
    private profileService: ProfileService,
    private storageService: BucketFireStorageService,
    private router: Router,
    private modalController: ModalController
  ) {
    this.id =+ this.route.snapshot.paramMap.get('id');
    this.route.queryParams.subscribe(params => {
      this.communityName = params['communityName'];
    });
    this.defaultHref = `tabs/feed/communities/community/${this.id}`;
    this.loadCommunityMembers();
  } 

  ngOnInit() {
    this.getProfilePic()
  }

  private getProfilePic() {
    this.profileService
      .getProfile()
      .then((response: Observable<any>) => {
        response.subscribe({
          next: async (profile: Profile) => {
            // Loop through existing communityUsers to find matching username
            for (let user of this.communityUsers) {
              if (user.username === profile.username) {
                this.myRole = user.role;
                this.myUsername = user.username;
                console.log('My role: ',this.myRole);
                
                break;
              }
            }
          },
          error: (err) => {
            console.error('Error fetching profile:', err);
          }
        });
      })
      .catch((error) => {
        console.error('Error in getProfile promise:', error);
      });
  }

  private async loadCommunityMembers() {
    try {
        const usersObservable = await this.communityService.getCommunityUsers(this.id);
        usersObservable.subscribe({
            next: (users) => {
                // Flatten nested array if necessary
                if (Array.isArray(users) && users.length === 1 && Array.isArray(users[0])) {
                    this.communityUsers = users[0];
                } else if (Array.isArray(users)) {
                    this.communityUsers = users;
                } else {
                    console.error('Unexpected response format:', users);
                }
                this.communityUsersAll = this.communityUsers;

                // Sort the users by role after loading
                this.communityUsers = this.sortUsersByRole(this.communityUsers);

                // Optionally, group users after loading
                this.groupedCommunityUsers = this.groupUsersIntoRows(this.communityUsers);

                // Preload additional data or images
                this.preloadImageUrls().then(() => {
                    console.log('Community members after preloading images:', this.communityUsers);
                });
            },
            error: (error) => console.error('Error fetching community members:', error)
        });
    } catch (error) {
        console.error('Failed to fetch community members:', error);
    }
  }

  private sortUsersByRole(users: CommunityUser[]): CommunityUser[] {
    return users.sort((a, b) => {
        // Define the order of roles
        const roleOrder = [1, 2, 3, 4];
        return roleOrder.indexOf(a.role) - roleOrder.indexOf(b.role);
    });
  }

  searchMembers() {
    if (this.searchTerm.trim() !== '') {
        const lowerCaseSearchTerm = this.searchTerm.toLowerCase();

        // Filter the flat array of community users by username
        this.communityUsers = this.communityUsersAll.filter(
            user => user.username.toLowerCase().includes(lowerCaseSearchTerm)
        );

        // Re-group the filtered users
        this.groupedCommunityUsers = this.groupUsersIntoRows(this.communityUsers);
    } else {
        // Restore the original list of community users
        this.communityUsers = [...this.communityUsersAll];
        // Re-group all users into the initial state
        this.groupedCommunityUsers = this.groupUsersIntoRows(this.communityUsers);
    }
  }

  private groupUsersIntoRows(users: CommunityUser[]): CommunityUser[][] {
      const groupedUsers = [];
      for (let i = 0; i < users.length; i += 3) {
          groupedUsers.push(users.slice(i, i + 3));
      }
      // Adjust the last group if it contains only one user
      if (groupedUsers.length > 1 && groupedUsers[groupedUsers.length - 1].length === 1) {
          groupedUsers[groupedUsers.length - 1].unshift(groupedUsers[groupedUsers.length - 2].pop());
      }
      return groupedUsers;
  }


  async preloadImageUrls() {
    for (let i = 0; i < this.communityUsers.length; i++) {
      if (!this.communityUsers[i].imageUrl && this.communityUsers[i].profilePic) {
        this.communityUsers[i].imageUrl = await this.getBucketUrl(this.communityUsers[i].profilePic, i);
      }
    }
  }

  async getBucketUrl(imageUrl: string, index: number): Promise<string> {
    try {
      if (this.cachedImageUrls[index]) {
        return this.cachedImageUrls[index];
      } else {
        const imageUrlFromService = await this.storageService.getBucketUrl(imageUrl);
        this.communityUsers[index].imageUrl = imageUrlFromService;
        this.cachedImageUrls[index] = imageUrlFromService;
        return imageUrlFromService;
      }
    } catch (error) {
      console.error('Error fetching image URL:', error);
      return '/path/to/default/image.jpg'; // Default image path if an error occurs
    }
  }

  getRoleClass(role: number): string {
    switch (role) {
      case 1:
        return 'super-admin';
      case 2:
        return 'admin';
      case 3:
        return 'moderator';
      default:
        return 'member';
    }
  }  

  calculateOptionsBreakpoint(visibleOptionsCount: number): number {
    // Define your breakpoints
    const breakpoints = [0.11, 0.17, 0.23, 0.29, 0.35, 0.41, 0.47];

    // Use the visibleOptionsCount as an index to select the breakpoint
    // Adjust for 0-based indexing and ensure it doesn't exceed the array bounds
    const index = Math.min(visibleOptionsCount - 1, breakpoints.length - 1);

    // Return the corresponding breakpoint
    return breakpoints[index];
  }

  async openOptions(user) {
    if (user.username == this.myUsername) {
      return;
    }

    // Configure visibility based on ownership
    const optionVisibility = {
      showViewProfile: true,
      showShareProfile: true,
      showPromoteOwner: this.myRole == 2,
      showPromoteModerator: user.role != 3 && this.myRole == 2,
      showDemoteModerator: user.role == 3 && this.myRole == 2,
      showReportMember: true,
      showBlockMember: this.myRole == 2 || this.myRole == 3,
      showRemoveMember: this.myRole == 2 || this.myRole == 3
    };

    // Calculate the number of visible options
    const visibleOptionsCount = Object.values(optionVisibility).filter(Boolean).length;

    // Determine the initial breakpoint based on the number of visible options
    const initialBreakpoint = this.calculateOptionsBreakpoint(visibleOptionsCount);

    // Create the modal with OptionMenuComponent, passing the visibility configuration and calculated initial breakpoint
    const modal = await this.modalController.create({
      component: OptionMenuComponent,
      cssClass: 'option-modal',
      componentProps: {
        optionVisibility: optionVisibility,
      },
      backdropDismiss: true,
      initialBreakpoint: initialBreakpoint, // Set the calculated initial breakpoint
      breakpoints: [0.11, 0.17, 0.23, 0.29, 0.35, 0.41, 0.47]
    });

    // Present the modal
    await modal.present();

    const { data: selectedOption } = await modal.onDidDismiss();
    if (selectedOption) {
      this.handleOptionSelection(selectedOption, user);
    }
  }

  handleOptionSelection(selectedOption: string, user) {
    switch (selectedOption) {
      case 'viewProfile':
        this.openProfile(user.id)
        break;
      
      case 'promoteOwner':
        this.promoteToOwner(user.username);
        break;

      case 'promoteModerator':
        this.promoteToModerator(user.id);
        break;
      
      case 'demoteModerator':
        this.demoteModerator(user.id);
        break;

      case 'removeMember':
        this.removeUser(user.id);
        break;

      // Handle other options...
      default:
        console.warn('Unknown option selected');
    }
  }

  openProfile(username: string) {
    this.router.navigate(['tabs/profile/public-profile/', username])
  }

  async removeUser(userId) {
    try {
      const response = await this.communityService.removeCommunityUser(this.id, userId);
      console.log('Remove response:', response);
      if (response.success) {
        this.removeUserFromArray(userId);
      }
    } catch (error) {
      console.error('Error confirming request:', error);
    }
  }

  private removeUserFromArray(userId) {
    const temp = this.communityUsers.filter(user => user.userId !== userId);
    this.groupedCommunityUsers = []
    temp.forEach(() => {
    this.groupedCommunityUsers.push(temp)
    })
    this.groupedCommunityUsers = this.groupUsersIntoRows(this.communityUsers);
    console.log('Updated community requests:', this.groupedCommunityUsers);
  }

  async promoteToOwner(username) {
    try {
      const response = await this.communityService.promoteToOwner(this.id, username);
      console.log('Remove response:', response);
      if (response.success) {
        this.updateUserRole(username, 2);
        this.updateUserRole(this.myUsername, 3);
        this.myRole = 3;
      } 
    } catch (error) {
      console.error('Error confirming request:', error);
    }
  }

  async promoteToModerator(userId) {
    try {
      const response = await this.communityService.promoteToModerator(this.id, userId);
      console.log('Remove response:', response);
      if (response.success) {
        this.updateUserRole(userId, 3);
      } 
    } catch (error) {
      console.error('Error confirming request:', error);
    }
  }

  async demoteModerator(userId) {
    try {
      const response = await this.communityService.demoteFromModerator(this.id, userId);
      console.log('Remove response:', response);
      if (response.success) {
        this.updateUserRole(userId, 4);
      } 
    } catch (error) {
      console.error('Error confirming request:', error);
    }
  }

  private updateUserRole(username, newRoleId) {
    let user = this.communityUsers.find(u => u.username === username);
    if (user) {
      user.role = newRoleId;
      // Optionally, trigger view update if needed
      this.communityUsers = [...this.communityUsers];
    }
  }

  ngOnDestroy() {
    // Unsubscribe from all subscriptions to avoid memory leaks
    this.subscriptions.unsubscribe();
  }
}
