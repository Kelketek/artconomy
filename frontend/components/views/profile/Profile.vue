<template>
  <v-container fluid>
    <ac-load-section :controller="subjectHandler.user">
      <template #default>
        <ac-profile-header
          :username="username"
          :show-edit="route.name === 'AboutUser'"
          :dense="true"
        />
        <v-card>
          <ac-tab-nav :items="items" label="See more" />
        </v-card>
        <router-view class="pa-0" :class="{ 'pt-3': needsSpace }" />
      </template>
    </ac-load-section>
  </v-container>
</template>

<script setup lang="ts">
import { useSubject } from "@/mixins/subjective.ts"
import AcProfileHeader from "@/components/views/profile/AcProfileHeader.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcTabNav from "@/components/navigation/AcTabNav.vue"
import { flatten } from "@/lib/lib.ts"
import {
  mdiAccount,
  mdiAccountMultiple,
  mdiBasket,
  mdiEye,
  mdiHeart,
  mdiImageAlbum,
} from "@mdi/js"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { listenForList } from "@/store/lists/hooks.ts"
import { listenForProfile } from "@/store/profiles/hooks.ts"
import { listenForForm } from "@/store/forms/hooks.ts"
import { computed, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import type { SubjectiveProps } from "@/types/main"

const props = defineProps<SubjectiveProps>()
const { subjectHandler, subject } = useSubject({ props })
const { setError } = useErrorHandling()
const route = useRoute()
const router = useRouter()

subjectHandler.artistProfile.get().catch(setError)
listenForList(`${flatten(props.username)}-products`)
listenForList(`${flatten(props.username)}-art`)
listenForList(`${flatten(props.username)}-collection`)
listenForList(`${flatten(props.username)}-characters`)
listenForList(`${flatten(props.username)}-journals`)
listenForForm(`${flatten(props.username)}-newJournal`)
listenForForm("newUpload")
listenForProfile(".*")

const items = computed(() => {
  const itemEntries = [
    {
      value: {
        name: "AboutUser",
        params: { username: props.username },
      },
      icon: mdiAccount,
      title: "About",
    },
  ]
  if (subject.value && subject.value.artist_mode) {
    itemEntries.push({
      value: {
        name: "Products",
        params: { username: props.username },
      },
      icon: mdiBasket,
      title: "Products",
    })
  }
  itemEntries.push(
    {
      value: {
        name: "Characters",
        params: { username: props.username },
      },
      icon: mdiAccountMultiple,
      title: "Characters",
    },
    {
      value: {
        name: "Gallery",
        params: { username: props.username },
      },
      icon: mdiImageAlbum,
      title: "Gallery",
    },
    {
      value: {
        name: "Favorites",
        params: { username: props.username },
      },
      icon: mdiHeart,
      title: "Favorites",
    },
    {
      value: {
        name: "Watchlists",
        params: { username: props.username },
      },
      icon: mdiEye,
      title: "Watchlists",
    },
  )
  return itemEntries
})

const needsSpace = computed(() => {
  return (
    [
      "Gallery",
      "Art",
      "ManageArt",
      "Collection",
      "ManageCollection",
      "Watchers",
      "Watching",
      "Watchlists",
    ].indexOf(String(route.name) + "") === -1
  )
})

const setDefaultRoute = () => {
  if (!subject.value) {
    return
  }
  if (route.name === "Profile") {
    router.replace({
      name: "AboutUser",
      params: { username: props.username },
    })
  }
}

watch(() => subject.value?.artist_mode, setDefaultRoute, {immediate: true})
watch(() => route.name, setDefaultRoute, {immediate: true})
</script>
