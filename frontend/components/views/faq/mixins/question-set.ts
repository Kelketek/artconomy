import {computed, nextTick, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useGoTo} from 'vuetify'


export const useQuestionSet = (questions: string[]) => {
  const router = useRouter()
  const route = useRoute()
  const routeName = route.name

  const attempts = ref(0)
  const goTo = useGoTo()

  const updatePath = (value: number) => {
    if (route.name != routeName) {
      // We've moved to a different route-- bail.
      return
    }
    const params: {[key: string]: any} = {}
    params.question = questions[value]
    const newParams = Object.assign({}, route.params, params)
    const newQuery = Object.assign({}, route.query)
    delete newQuery.page
    /* istanbul ignore next */
    const name = route.name || undefined
    const newPath = {name, params: newParams, query: newQuery}
    router.replace(newPath).then(() => {})
  }

  const scrollToQuestion = () => {
    attempts.value += 1
    if (!tab.value) {
      return
    }
    if (attempts.value > 10) {
      console.error(`Could not scroll to question number ${tab.value} with label '${route.params.question}'`)
      return
    }
    const index = tab.value + 1
    const selector = `.faq > .v-expansion-panels > .v-expansion-panel:nth-child(${index})`
    nextTick(() => {
      const target = document.querySelector(selector) as HTMLElement
      if (target === null) {
        scrollToQuestion()
        return
      }
      attempts.value = 0
      return goTo(target)
    }).then(() => {})
  }

  const tab = computed({
    get() {
      if (!route.params.question) {
        updatePath(0)
        return 0
      }
      return questions.indexOf(route.params.question as string)
    },
    set(value: number) {
      updatePath(value)
    },
  })
  onMounted(() => {
    scrollToQuestion()
  })
  return {
    tab,
    updatePath,
    scrollToQuestion,
  }
}
