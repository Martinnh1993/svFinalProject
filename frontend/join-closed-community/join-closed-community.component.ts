import { Component, OnInit } from '@angular/core';
import { ModalController } from '@ionic/angular';

@Component({
  selector: 'app-join-closed-community',
  templateUrl: './join-closed-community.component.html',
  styleUrls: ['./join-closed-community.component.scss'],
})
export class JoinClosedCommunityComponent{

  constructor(
    private modalController: ModalController
  ) { }

  request() {
    this.modalController.dismiss({
      'result': 'request'
    });
  }

  cancel() {
    this.modalController.dismiss({
      'result': 'cancel'
    });
  }

}
