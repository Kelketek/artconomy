import Component from 'vue-class-component'
import Vue from 'vue'
import {Prop, Watch} from 'vue-property-decorator'
import deepEqual from 'fast-deep-equal'

@Component
export default class Editable extends Vue {
  public scratch: any = ''

  @Prop({required: true})
  public value!: any

  @Prop({default: true})
  public autoSave!: boolean

  @Prop({default: null})
  public saveComparison!: string | null

  @Prop({default: true})
  public saveIndicator!: boolean

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
    const attrs = {...this.$attrs}
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
    if (typeof this.scratch !== 'string') {
      return deepEqual(this.scratch, this.saveComparison)
    }
    return this.saveComparison.trim() === this.scratch.trim()
  }
}
