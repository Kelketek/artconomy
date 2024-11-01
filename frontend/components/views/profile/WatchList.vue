<template>
  <ac-paginated :list="watch" :track-pages="true">
    <v-row>
      <v-col cols="3" sm="2" lg="1" v-for="user in watch.list" :key="user.x!.id">
        <ac-avatar :user="user.x" />
      </v-col>
    </v-row>
  </ac-paginated>
</template>

<script setup lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import {flatten} from '@/lib/lib.ts'
import {useList} from '@/store/lists/hooks.ts'
import type {SubjectiveProps} from '@/types/main'
import {TerseUser} from '@/store/profiles/types/main'

const props = defineProps<SubjectiveProps & {endpoint: string, nameSpace: string}>()
const watch = useList<TerseUser>(`${flatten(props.username)}__${props.nameSpace}`, {endpoint: props.endpoint})
watch.firstRun()
</script>
