<template>
  <router-link
    v-if="to && !newTab"
    v-bind="$props"
    :to="to"
    @click.capture="navigate"
  >
    <slot />
  </router-link>
  <a
    v-else-if="newTab && to"
    :href="`${to}`"
    target="_blank"
  >
    <slot />
  </a>
  <slot v-else />
</template>

<script setup lang="ts">
import {RouteLocationRaw, useRouter} from 'vue-router'
import {ArtState} from '@/store/artState.ts'
import {useStore} from 'vuex'

const props = withDefaults(defineProps<{
  to?: RouteLocationRaw|null,
  // Must be used only with string location
  newTab?: boolean
}>(), {newTab: false})

const router = useRouter()
const store = useStore<ArtState>()

const navigate = (event: Event) => {
  event.preventDefault()
  if (store.state.iFrame) {
    event.stopPropagation()
    const routeData = router.resolve(props.to!)
    window.open(routeData.href, '_blank')
    return
  }
  router.push(props.to!)
}
</script>
