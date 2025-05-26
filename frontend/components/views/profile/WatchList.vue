<template>
  <ac-paginated :list="watch" :track-pages="true">
    <v-row>
      <v-col v-for="user in watch.list" :key="user.x!.id" cols="3" md="1">
        <ac-profile-preview :user="user.x!" />
      </v-col>
    </v-row>
  </ac-paginated>
</template>

<script setup lang="ts">
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import { flatten } from "@/lib/lib.ts"
import { useList } from "@/store/lists/hooks.ts"
import type { SubjectiveProps } from "@/types/main"
import { TerseUser } from "@/store/profiles/types/main"
import AcProfilePreview from "@/components/AcProfilePreview.vue"

const props = defineProps<
  SubjectiveProps & { endpoint: string; nameSpace: string }
>()
const watch = useList<TerseUser>(
  `${flatten(props.username)}__${props.nameSpace}`,
  { endpoint: props.endpoint },
)
watch.firstRun()
</script>
