<!--suppress JSUnusedLocalSymbols -->
<template>
  <slot :on="on">
    <v-btn class="confirm-launch" variant="flat" @click="show">Submit</v-btn>
  </slot>
  <v-dialog v-model="showModal" max-width="500px" :persistent="sending" :attach="$modalTarget">
    <v-card :class="cardClass">
      <v-toolbar flat dark color="secondary">
        <v-toolbar-title>
          <slot name="title">Are you sure?</slot>
        </v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click="showModal=false" dark class="dialog-closer">
          <v-icon :icon="mdiClose"/>
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
        <v-btn variant="flat" @click.stop="showModal=false" :disabled="sending" class="cancel-button">
          <slot name="cancel-text">Cancel</slot>
        </v-btn>
        <v-btn variant="flat" color="red" @click.stop="submit" :disabled="sending" class="confirmation-button">
          <slot name="confirm-text">Yes, I am sure.</slot>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
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
import {Component, Prop, toNative} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'
import {mdiClose} from '@mdi/js'

@Component
class AcConfirmation extends ArtVue {
  @Prop({required: true})
  public action!: () => Promise<any>

  @Prop()
  public cardClass!: string

  public showModal: boolean = false
  public sending: boolean = false
  public mdiClose = mdiClose

  public dismiss() {
    this.showModal = false
    this.sending = false
  }

  public get cardClassLiteral() {
    return `${this.cardClass} ${this.showModal ? 'confirmation-modal-active' : ''}`
  }

  public show(event: Event) {
    event.stopPropagation()
    this.showModal = true
  }

  public submit() {
    this.sending = true
    this.action().finally(this.dismiss)
  }

  public get on() {
    return {click: this.show}
  }
}

export default toNative(AcConfirmation)
</script>
