<!--suppress XmlUnboundNsPrefix -->
<template>
  <v-flex class="ac-editor">
    <v-layout row wrap>
      <v-flex xs12 v-if="previewMode">
        <v-layout row wrap>
          <ac-rendered xs12 :value="scratch" class="editor-preview"></ac-rendered>
        </v-layout>
      </v-flex>
      <v-flex xs12 v-else>
        <v-textarea v-bind="inputAttrs" ref="input" v-model="scratch" outline :auto-grow="autoGrow" :rows="rows || this.defaultRows">
        </v-textarea>
      </v-flex>
      <v-flex xs12>
        <v-layout wrap>
          <v-flex shrink>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn icon v-on="on" @click="previewMode = !previewMode" class="preview-mode-toggle" :class="{weakened: disabled}" color="grey darken-4">
                  <v-icon v-if="previewMode">visibility_off</v-icon>
                  <v-icon v-else>visibility</v-icon>
                </v-btn>
              </template>
              <span>Preview</span>
            </v-tooltip>
          </v-flex>
          <v-flex shrink>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn v-on="on" @click="setMarkdownHelp(true)" :class="{weakened: disabled}" icon color="blue lighten-2"><v-icon>help</v-icon></v-btn>
              </template>
              <span>Formatting help</span>
            </v-tooltip>
          </v-flex>
          <v-spacer>
          </v-spacer>
          <slot name="pre-actions" :disabled="disabled"></slot>
          <slot name="actions">
            <v-flex shrink>
              <v-layout row>
                <v-spacer></v-spacer>
                <v-flex shrink>
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
                </v-flex>
                <v-flex v-if="!autoSave" shrink>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn v-on="on" @click="save" :disabled="saved || disabled" icon color="black" class="save-button">
                        <v-icon color="yellow">save</v-icon>
                      </v-btn>
                    </template>
                    <span>Save</span>
                  </v-tooltip>
                </v-flex>
              </v-layout>
            </v-flex>
          </slot>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-flex>
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

    @Prop({default: 0})
    public rows!: number

    @Mutation('setMarkdownHelp')
    public setMarkdownHelp: any

    public previewMode = false
    public markdownHelp = false

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

    public get inputAttrs() {
      const attrs: any = {...this.$attrs}
      attrs.disabled = this.disabled
      delete attrs.value
      delete attrs.autoSave
      return attrs
    }

    public get defaultRows() {
      return this.value.split(/\r\n|\r|\n/).length
    }

    public get saved() {
      if (this.saveComparison === null) {
        return false
      }
      return this.saveComparison.trim() === this.scratch.trim()
    }
}
</script>