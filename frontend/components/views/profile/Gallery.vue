<template>
  <v-container :id="id" fluid class="pa-0">
    <v-card>
      <ac-tab-nav :items="items" label="Select gallery" />
    </v-card>
    <v-row v-if="controls" class="d-flex align-content-end">
      <v-col class="text-center mt-3 text-md-right">
        <v-btn
          v-if="artPage || collectionPage"
          color="green"
          class="mx-2"
          variant="flat"
          @click="showUpload = true"
        >
          <v-icon left :icon="mdiPlus" />
          New Submission
        </v-btn>
        <v-btn color="primary" variant="flat" @click="managing = !managing">
          <v-icon left :icon="mdiCog" />
          <span v-if="managing">Finish</span>
          <span v-else>Manage</span>
        </v-btn>
      </v-col>
    </v-row>
    <router-view
      v-if="subject"
      :key="`${username}-${String(route.name)}`"
      class="pa-0 pt-3"
    />
    <ac-new-submission
      ref="newSubmissionForm"
      v-model="showUpload"
      :username="username"
      :allow-multiple="true"
      @success="postAdd"
    />
  </v-container>
</template>

<script setup lang="ts">
import { flatten, genId } from "@/lib/lib.ts"
import { useUpload } from "@/mixins/upload.ts"
import AcTabNav from "@/components/navigation/AcTabNav.vue"
import { computed, ref, watch } from "vue"
import { mdiCog, mdiImageMultiple, mdiPalette, mdiPlus } from "@mdi/js"
import { useList } from "@/store/lists/hooks.ts"
import { useRoute, useRouter } from "vue-router"
import { useSubject } from "@/mixins/subjective.ts"
import AcNewSubmission from "@/components/AcNewSubmission.vue"
import type {
  ArtistTag,
  SubjectiveProps,
  Submission,
  TabNavSpec,
} from "@/types/main"

const props = defineProps<SubjectiveProps>()
const { subject, controls } = useSubject({ props })
const route = useRoute()
const router = useRouter()
const id = ref(genId())
const newSubmissionForm = ref<null | typeof AcNewSubmission>(null)

const art = useList<ArtistTag>(`${props.username}-art`, {
  endpoint: `/api/profiles/account/${props.username}/submissions/art/`,
})
const collection = useList<Submission>(
  `${flatten(props.username)}-collection`,
  {
    endpoint: `/api/profiles/account/${props.username}/submissions/collection/`,
  },
)
// Conditionally fetch. If we're on these pages, we want to give the paginator a chance to set the page before
// fetching. Otherwise we want to prefetch in case the user switches tabs.

const artPage = computed(() => {
  return route.name === "Art"
})

const collectionPage = computed(() => {
  return route.name === "Collection"
})

if (!artPage.value) {
  art.firstRun().then()
}
if (!collectionPage.value) {
  collection.firstRun().then()
}
if (route.name === "Gallery") {
  router.push({
    name: "Art",
    params: { username: props.username },
  })
}

const num = (val: number | null) => (typeof val === "number" ? val : undefined)

const items = computed<TabNavSpec[]>(() => {
  return [
    {
      value: {
        name: "Art",
        params: { username: props.username },
      },
      count: num(art.count),
      icon: mdiPalette,
      title: `${possessive.value} Art`,
    },
    {
      value: {
        name: "Collection",
        params: { username: props.username },
      },
      count: num(collection.count),
      icon: mdiImageMultiple,
      title: `${possessive.value} Collection`,
    },
  ]
})

const possessive = computed(() => {
  if (props.username.endsWith("s")) {
    return `${props.username}'`
  } else {
    return `${props.username}'s`
  }
})

const { showUpload } = useUpload()

watch(showUpload, () => {
  if (newSubmissionForm.value) {
    newSubmissionForm.value.isArtist = artPage.value
  }
})

const groups = {
  collection,
  art,
} as const

const managing = computed({
  get() {
    return String(route.name).includes("Manage")
  },
  set(val: boolean) {
    const newRoute = {
      name: String(route.name) + "",
      params: route.params,
      query: route.query,
    }
    if (val && !managing.value) {
      newRoute.name = "Manage" + String(route.name)
    } else if (!val && managing.value) {
      for (const group of ["collection", "art"] as Array<keyof typeof groups>) {
        if (newRoute.name.toLowerCase().includes(group)) {
          groups[group].get()
        }
      }
      collection.get()
      art.get()
      newRoute.name = newRoute.name.replace("Manage", "")
    }
    router.replace(newRoute)
  },
})

const postAdd = (submission: Submission | ArtistTag) => {
  const routeName = String(route.name) + ""
  for (const group of ["collection", "art"] as Array<keyof typeof groups>) {
    if (
      routeName.toLowerCase().includes(group) &&
      groups[group].currentPage === 1
    ) {
      groups[group].unshift(submission as Submission & ArtistTag)
    }
  }
}
</script>

<style>
.gallery-container {
  position: relative;
}
</style>
