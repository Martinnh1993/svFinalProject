import { Component, OnInit } from '@angular/core';
import { ModalController } from '@ionic/angular';

@Component({
  selector: 'app-create-community-popup',
  templateUrl: './create-community-popup.component.html',
  styleUrls: ['./create-community-popup.component.scss'],
})
export class CreateCommunityPopupComponent {

  constructor
  (
    private modalController: ModalController
  ) 
  {}

  continue() {
    this.modalController.dismiss({
      'result': 'continue'
    });
  }

  cancel() {
    this.modalController.dismiss({
      'result': 'cancel'
    });
  }
}
