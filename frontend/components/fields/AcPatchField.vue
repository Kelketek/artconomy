<!--suppress XmlUnboundNsPrefix -->
<template>
  <component :is="fieldType" v-bind="inputAttrs" v-on="$listeners" v-model="scratch" v-if="(patcher.loaded || patcher.model)" @keydown.enter="enterHandler" class="patch-field">
    <slot v-for="(_, name) in $slots" :name="name" :slot="name"/>
    <v-flex slot="append" v-if="!handlesSaving">
      <v-layout>
        <v-tooltip top v-if="saved && saveIndicator">
          <template v-slot:activator="{ on }">
            <!-- Using a button here so the two elements are aligned. -->
            <v-btn v-on="on" icon class="save-indicator" @click.stop="() => {}" :ripple="false" tabindex="-1">
              <v-icon color="green" class="save-indicator">check_circle</v-icon>
            </v-btn>
          </template>
          <span>Saved</span>
        </v-tooltip>
        <v-tooltip top v-else-if="saveIndicator">
          <template v-slot:activator="{ on }">
            <!-- Using a button here so the two elements are aligned. -->
            <v-btn v-on="on" icon class="save-indicator" @click.stop="() => {}" :ripple="false" tabindex="-1" :disabled="disabled">
              <v-icon color="yellow" class="save-indicator">warning</v-icon>
            </v-btn>
          </template>
          <span>Unsaved</span>
        </v-tooltip>
        <v-tooltip top v-if="!autoSave">
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" @click="save" :disabled="saved || disabled" icon color="black" class="save-button">
              <v-icon color="yellow">save</v-icon>
            </v-btn>
          </template>
          <span>Save</span>
        </v-tooltip>
      </v-layout>
    </v-flex>
  </component>
</template>

<style lang="stylus">
  .save-indicator {
    &.v-btn--active::before,
    &.v-btn:hover::before, &.v-btn:focus::before {
      background-color: unset;
    }
  }
</style>

<script lang="ts">
import {Prop, Watch} from 'vue-property-decorator'
import Component from 'vue-class-component'
import Vue from 'vue'
import {Patch} from '@/store/singles/patcher'
import deepEqual from 'fast-deep-equal'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcRatingField from '@/components/fields/AcRatingField.vue'
import AcUppyFile from '@/components/fields/AcUppyFile.vue'
import AcSubmissionSelect from '@/components/fields/AcSubmissionSelect.vue'
import AcBankToggle from '@/components/fields/AcBankToggle.vue'
import AcPriceField from '@/components/fields/AcPriceField.vue'
import AcStarField from '@/components/fields/AcStarField.vue'

@Component({components: {
  AcStarField,
  AcPriceField,
  AcBankToggle,
  AcSubmissionSelect,
  AcUppyFile,
  AcRatingField,
  AcTagField,
  AcEditor,
}})
export default class AcPatchField extends Vue {
    @Prop({default: 'v-text-field'})
    public fieldType!: string
    @Prop({required: true})
    public patcher!: Patch
    @Prop({default: true})
    public saveIndicator!: boolean
    @Prop({default: true})
    public autoSave!: boolean
    @Prop({default: false})
    public enterSave!: boolean
    @Prop()
    public id!: string

    public scratch: any = ''

    public created() {
      this.scratch = this.patcher.model
    }

    public save() {
      if (!this.saved) {
        this.patcher.setValue(this.scratch)
      }
    }

    @Watch('scratch')
    public watchScratch(val: any) {
      if (this.autoSave || this.handlesSaving) {
        this.save()
      }
    }

    @Watch('patcher.model')
    public watchValue(val: any) {
      if (this.autoSave || this.handlesSaving) {
        this.scratch = val
      }
    }

    @Watch('patcher.cached')
    public watchCache(val: any) {
      // A synced handler is modifying our value.
      this.scratch = val
    }

    @Watch('patcher.errors')
    public errorCheck(val: string[]) {
      if (val.length && !this.autoSave) {
        // When we have an error, our cache will still have the new value. We need to reset it so that our child
        // component knows we've still not saved what's upstream. Note: This is only for child components that handle
        // their own save events, such as the editor. Doing this on other components runs the risk of wiping out
        // the value the user set. To override this, set refresh to false.
        this.scratch = this.patcher.rawValue
      }
    }

    public enterHandler(event: Event) {
      if (!this.enterSave) {
        return
      }
      this.save()
    }

    public get saved() {
      let result: boolean
      if (typeof this.scratch !== 'string') {
        result = deepEqual(this.scratch, this.patcher.rawValue)
        if (result) {
          this.patcher.errors = []
        }
        return result
      }
      if (typeof this.patcher.rawValue === 'number') {
        return parseFloat(this.scratch) === this.patcher.rawValue
      }
      if (typeof this.patcher.rawValue !== 'string') {
        // Can't be saved if it's not the same type.
        return false
      }
      result = this.patcher.rawValue.trim() === this.scratch.trim()
      if (result) {
        this.patcher.errors = []
      }
      return result
    }

    public get disabled() {
      return Boolean(this.$attrs.disabled || (!this.autoSave && this.patcher.patching))
    }

    public get loading() {
      if (this.autoSave) {
        return false
      }
      if (this.patcher.patching) {
        return (this.$vuetify.theme.secondary as any).base
      }
    }

    public get handlesSaving() {
      // May want to find a way to generalize this in the future.
      return this.fieldType === 'ac-editor'
    }

    public get inputAttrs() {
      const attrs: any = {...this.$attrs}
      delete attrs.value
      attrs.errorMessages = this.patcher.errors
      attrs.disabled = this.disabled
      attrs.loading = this.loading
      attrs.id = this.id
      if (this.handlesSaving) {
        attrs.autoSave = this.autoSave
        attrs.saveIndicator = this.saveIndicator
        attrs.saveComparison = this.patcher.rawValue
      }
      return attrs
    }
}
</script>
