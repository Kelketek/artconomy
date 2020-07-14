<!--suppress JSUnusedLocalSymbols -->
<template>
  <fragment>
    <slot :on="on">
      <v-btn class="confirm-launch" @click="show">Submit</v-btn>
    </slot>
    <v-dialog v-model="showModal" max-width="500px" :persistent="sending">
      <v-card :class="cardClass">
        <v-toolbar flat dark color="secondary">
          <v-toolbar-title><slot name="title">Are you sure?</slot></v-toolbar-title>
          <v-spacer/>
          <v-btn icon @click.native="showModal=false" dark class="dialog-closer">
            <v-icon>close</v-icon>
          </v-btn>
        </v-toolbar>
        <div class="loading-overlay" v-if="sending">
          <v-progress-circular
              indeterminate
              :size="70"
              :width="7"
              color="purple"
          />
        </div>
        <v-card-text :class="{'confirm-submitting': sending}">
          <slot name="confirmation-text">
            This cannot be undone.
          </slot>
          <v-spacer/>
        </v-card-text>
        <v-card-actions right :class="{'confirm-submitting': sending}">
          <v-spacer></v-spacer>
          <v-btn @click.stop="showModal=false" :disabled="sending" class="cancel-button">
            <slot name="cancel-text">Cancel</slot>
          </v-btn>
          <v-btn color="red" @click.stop="submit" :disabled="sending" class="confirmation-button">
            <slot name="confirm-text">Yes, I am sure.</slot>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </fragment>
</template>

<style>
  .loading-overlay {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    top: 0;
    right: 0;
    height: 100%;
    width: 100%;
    vertical-align: center;
    text-align: center;
    z-index: 205;
  }

  /*noinspection ALL*/
  .confirm-submitting {
    opacity: .4;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {Fragment} from 'vue-fragment'

@Component({components: {Fragment}})
export default class AcConfirmation extends Vue {
    @Prop({required: true})
    private action!: () => Promise<any>

    @Prop()
    private cardClass!: string

    private showModal: boolean = false
    private sending: boolean = false

    private dismiss() {
      this.showModal = false
      this.sending = false
    }

    private show(event: Event) {
      event.stopPropagation()
      this.showModal = true
    }

    private submit() {
      this.sending = true
      const promise = this.action()
      // May not be a promise in the case of tests.
      if (promise && promise.finally) {
        promise.finally(this.dismiss)
      } else {
        this.dismiss()
      }
    }

    private get on() {
      return {click: this.show}
    }
}
</script>
