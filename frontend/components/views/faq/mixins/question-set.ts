import Vue from 'vue'
import Component from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import {Mutation} from 'vuex-class'

@Component
export default class QuestionSet extends Vue {
  public tab!: number
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public attempts: number = 0
  @Mutation('supportDialog') public setSupport: any

  // It will be hard to know if this is correct until production. For now, ignoring in code coverage.
  /* istanbul ignore next */
  public scrollToQuestion() {
    this.attempts += 1
    if (!this.tab) {
      return
    }
    if (this.attempts > 10) {
      console.error(`Could not scroll to question number ${this.tab} with label '${this.$route.params.question}'`)
      return
    }
    const index = this.tab + 1
    const selector = `.faq > .v-expansion-panels > .v-expansion-panel:nth-child(${index})`
    this.$nextTick(() => {
      const target = document.querySelector(selector)
      if (target === null) {
        this.scrollToQuestion()
        return
      }
      this.attempts = 0
      target.scrollIntoView({block: 'center', behavior: 'smooth'})
    })
  }

  public mounted() {
    this.scrollToQuestion()
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.pricing.get().then()
  }
}
