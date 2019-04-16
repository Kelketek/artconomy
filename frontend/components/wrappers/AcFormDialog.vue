<template>
  <v-dialog
      v-model="toggle"
      :fullscreen="fullscreen"
      ref="dialog"
      :transition="transition"
      :overlay="false"
      :persistent="persistent"
      scrollable
      :width="width"
  >
    <v-card tile :id="id">
      <v-toolbar card dark color="secondary" v-if="$vuetify.breakpoint.smAndDown">
        <v-btn icon @click.native="toggle = false" dark class="dialog-closer">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{title}}</v-toolbar-title>
        <v-spacer/>
        <slot name="top-buttons">
          <v-toolbar-items v-if="$vuetify.breakpoint.smAndDown">
            <v-btn flat @click.prevent="reSend" :disabled="disabled">{{ submitText }}</v-btn>
          </v-toolbar-items>
        </slot>
      </v-toolbar>
      <v-toolbar card dark color="secondary" dense v-else>
        <v-toolbar-title>{{title}}</v-toolbar-title>
        <v-spacer/>
        <v-btn icon @click.native="toggle = false" dark class="dialog-closer">
          <v-icon>close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text class="scrollableText" :class="{'pa-0': fluid}">
        <v-form @submit.prevent="reSend">
          <slot name="header"/>
          <ac-form-container
              :errors="errors"
              :sending="sending"
          >
            <slot/>
          </ac-form-container>
          <slot name="footer"/>
          <slot name="bottom-buttons">
            <v-card-actions row wrap class="hidden-sm-and-down">
                <v-spacer></v-spacer>
                <v-btn @click.native="toggle=false">Cancel</v-btn>
                <v-btn color="primary" type="submit" :disabled="disabled" class="dialog-submit">{{ submitText }}
                </v-btn>
            </v-card-actions>
          </slot>
        </v-form>
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

  @Component({
    name: 'ac-form-dialog',
    components: {AcFormContainer},
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
    @Prop({default: ''})
    public title!: string
    @Prop()
    public submit!: () => void
    @Prop()
    public id!: string
    @Prop({default: false})
    public fluid!: boolean

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
