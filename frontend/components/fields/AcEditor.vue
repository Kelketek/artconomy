<!--suppress XmlUnboundNsPrefix -->
<template>
  <div class="flex ac-editor">
    <v-row no-gutters>
      <v-col cols="12" v-if="previewMode">
        <v-row no-gutters  >
          <ac-rendered :value="scratch" :classes="{'editor-preview': true, col: true}" />
        </v-row>
      </v-col>
      <v-col cols="12" v-else>
        <v-textarea v-bind="inputAttrs" ref="input" v-model="scratch" outlined :auto-grow="autoGrow" :error-messages="errorMessages" />
      </v-col>
      <v-col cols="12">
        <v-row dense>
          <v-col class="shrink" >
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn fab small v-on="on" @click="previewMode = !previewMode" class="preview-mode-toggle" :class="{weakened: disabled}" color="grey darken-4">
                  <v-icon v-if="previewMode">visibility_off</v-icon>
                  <v-icon v-else>visibility</v-icon>
                </v-btn>
              </template>
              <span>Preview</span>
            </v-tooltip>
          </v-col>
          <v-col class="shrink" >
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn v-on="on" @click="setMarkdownHelp(true)" :class="{weakened: disabled}" fab small color="blue lighten-2"><v-icon>help</v-icon></v-btn>
              </template>
              <span>Formatting help</span>
            </v-tooltip>
          </v-col>
          <v-spacer>
          </v-spacer>
          <slot name="actions">
            <v-col>
              <v-row dense>
                <v-spacer />
                <slot name="pre-actions" :disabled="disabled" />
                <v-col class="shrink">
                  <v-tooltip top v-if="saved && saveIndicator">
                    <template v-slot:activator="{ on }">
                      <!-- Using a button here so the two elements are aligned. -->
                      <v-btn v-on="on" icon class="save-indicator" @click.stop="() => {}" :ripple="false" tabindex="-1" :disabled="disabled">
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
                </v-col>
                <v-col class="shrink" v-if="!autoSave" >
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn v-on="on" @click="save" :disabled="saved || disabled" color="black" fab small class="save-button">
                        <v-icon color="yellow">save</v-icon>
                      </v-btn>
                    </template>
                    <span>Save</span>
                  </v-tooltip>
                </v-col>
              </v-row>
            </v-col>
          </slot>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>

<style lang="stylus">
  .save-indicator {
    &.v-btn--active::before,
    &.v-btn:hover::before, &.v-btn:focus::before {
      background-color: unset;
    }
  }
  .weakened {
    opacity: .25
  }
</style>

<script lang="ts">
import Vue from 'vue'
import {Prop, Watch} from 'vue-property-decorator'
import Component from 'vue-class-component'
import AcMarkdownExplanation from '@/components/fields/AcMarkdownExplination.vue'
import {Mutation} from 'vuex-class'
import AcRendered from '@/components/wrappers/AcRendered'
  @Component({
    components: {AcRendered, AcMarkdownExplanation},
  })
export default class AcEditor extends Vue {
    @Prop({required: true})
    public value!: string

    @Prop({default: true})
    public autoSave!: boolean

    @Prop({default: null})
    public saveComparison!: string | null

    @Prop({default: true})
    public autoGrow!: boolean

    @Prop({default: true})
    public saveIndicator!: boolean

    @Prop({default: false})
    public disabled!: boolean

    @Prop({default: () => []})
    public errorMessages!: string[]

    @Mutation('setMarkdownHelp')
    public setMarkdownHelp: any

    public previewMode = false

    public scratch: string = ''

    public created() {
      this.scratch = this.value
    }

    public save() {
      this.$emit('input', this.scratch)
    }

    @Watch('scratch')
    public watchScratch(val: string) {
      if (this.autoSave) {
        this.save()
      }
    }

    @Watch('value')
    public watchValue(val: string) {
      if (this.autoSave) {
        this.scratch = val
      }
    }

    public triggerResize() {
      // Only reliable way to trigger a resize is to tell the internal text element that an input event has occurred.
      const inputElement = this.$refs.input as Vue
      inputElement.$el.querySelector('textarea')!.dispatchEvent(new Event('input'))
    }

    @Watch('$route.query.editing')
    public editingResize() {
      // Most cases where we need to have a text area hidden, we use v-show, which makes calculation of field height
      // impossible.
      //
      // In those cases, watch for the editing flag to be flipped and resize if so.
      this.triggerResize()
    }

    @Watch('autoGrow')
    public autoGrowResize() {
      // Hacky workaround for v-show. Use the same boolean for v-show as for this to force a recalculation when
      // changed.
      this.triggerResize()
    }

    public get inputAttrs() {
      const attrs: any = {...this.$attrs}
      attrs.disabled = this.disabled
      delete attrs.value
      delete attrs.autoSave
      return attrs
    }

    public get saved() {
      if (this.saveComparison === null) {
        return false
      }
      return this.saveComparison.trim() === this.scratch.trim()
    }
}
</script>
