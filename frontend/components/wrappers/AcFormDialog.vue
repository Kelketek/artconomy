<template>
  <v-dialog
      v-model="toggle"
      :fullscreen="fullscreen"
      ref="dialog"
      :transition="transition"
      :persistent="persistent"
      scrollable
      :eager="eager"
      :width="width"
  >
    <v-card :id="id">
      <div v-if="$vuetify.breakpoint.smAndDown">
        <v-toolbar dark color="secondary">
          <v-btn icon @click.native="toggle = false" dark class="dialog-closer">
            <v-icon>close</v-icon>
          </v-btn>
          <v-toolbar-title>{{title}}</v-toolbar-title>
          <v-spacer/>
          <slot name="top-buttons">
            <v-toolbar-items v-if="$vuetify.breakpoint.smAndDown">
              <v-btn text @click.prevent="reSend" :disabled="disabled">{{ submitText }}</v-btn>
            </v-toolbar-items>
          </slot>
        </v-toolbar>
      </div>
      <v-toolbar flat dark color="secondary" dense v-else>
        <v-toolbar-title>{{title}}</v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click.native="toggle = false" dark class="dialog-closer">
          <v-icon>close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text class="scrollableText" :class="{'pa-0': fluid}">
        <ac-form @submit.prevent="reSend">
          <v-container class="pa-0">
            <slot name="header" />
          </v-container>
          <ac-form-container
              :errors="errors"
              :sending="sending"
          >
            <slot/>
          </ac-form-container>
          <slot name="footer"/>
          <slot name="bottom-buttons" :show-submit="showSubmit">
            <v-card-actions row wrap class="hidden-sm-and-down">
                <v-spacer></v-spacer>
                <v-btn @click.native="toggle=false">{{ cancelText }}</v-btn>
                <v-btn color="primary" type="submit" :disabled="disabled" class="dialog-submit" v-if="showSubmit">{{ submitText }}
                </v-btn>
            </v-card-actions>
          </slot>
        </ac-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>
  .hidden {
    display: none;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import AcFormContainer from './AcFormContainer.vue'
import Dialog from '@/mixins/dialog'
import AcForm from '@/components/wrappers/AcForm.vue'

  @Component({
    name: 'ac-form-dialog',
    components: {AcForm, AcFormContainer},
  })
export default class AcFormDialog extends mixins(Dialog) {
    @Prop()
    public sending!: boolean

    @Prop()
    public disabled!: boolean

    @Prop()
    public errors!: string[]

    @Prop({default: 'Submit'})
    public submitText!: string

    @Prop({default: 'Cancel'})
    public cancelText!: string

    @Prop({default: ''})
    public title!: string

    @Prop()
    public submit!: () => void

    @Prop()
    public id!: string

    @Prop({default: false})
    public fluid!: boolean

    @Prop({default: false})
    public eager!: boolean

    @Prop({default: true})
    public showSubmit!: boolean

    public reSend(event: Event) {
      // Re-emit form so that we can use semantic Vue @event directives without the browser
      // refreshing the page on submission.
      this.$emit('submit', event)
    }

    /* istanbul ignore next */
    @Watch('value')
    public autofocus(val: boolean) {
      if (val) {
        this.$nextTick(() => {
          const element = document.querySelector(`#${this.id} input[autofocus]`) as HTMLElement
          if (!element) {
            return
          }
          element.focus()
        })
      }
    }
}
</script>
