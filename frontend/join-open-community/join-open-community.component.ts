import { Component } from '@angular/core';
import { ModalController } from '@ionic/angular';

@Component({
  selector: 'app-join-open-community',
  templateUrl: './join-open-community.component.html',
  styleUrls: ['./join-open-community.component.scss'],
})
export class JoinOpenCommunityComponent {

  constructor(
    private modalController: ModalController
  ) { }

  join() {
    this.modalController.dismiss({
      'result': 'join'
    });
  }

  cancel() {
    this.modalController.dismiss({
      'result': 'cancel'
    });
  }

}
