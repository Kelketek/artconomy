import {Component} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller.ts'
import Pricing from '@/types/Pricing.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component
export default class QuestionSet extends ArtVue {
  public questions: string[] = []
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public attempts: number = 0

  public updatePath(value: number) {
    const params: {[key: string]: any} = {}
    params.question = this.questions[value]
    const newParams = Object.assign({}, this.$route.params, params)
    const newQuery = Object.assign({}, this.$route.query)
    delete newQuery.page
    /* istanbul ignore next */
    const name = this.$route.name || undefined
    const newPath = {name, params: newParams, query: newQuery}
    this.$router.replace(newPath)
  }

  public get tab() {
    if (!this.$route.params.question) {
      this.updatePath(0)
      return 0
    }
    return this.questions.indexOf(this.$route.params.question as string)
  }

  public set tab(value) {
    this.updatePath(value)
  }

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
      target.scrollIntoView({
        block: 'center',
        behavior: 'smooth',
      })
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
