<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-col v-for="user in list.list" :key="user.x!.id" cols="3" md="2">
      <ac-profile-preview :user="user.x!" />
    </v-col>
  </ac-paginated>
</template>
<script setup lang="ts">
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import { useList } from "@/store/lists/hooks.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { useSearchList } from "@/components/views/search/mixins/SearchList.ts"
import { TerseUser } from "@/store/profiles/types/main"
import AcProfilePreview from "@/components/AcProfilePreview.vue"

const list = useList<TerseUser>("searchProfiles", {
  endpoint: "/api/profiles/search/user/",
  persistent: true,
})
const searchForm = useForm("search")
useSearchList(searchForm, list)
</script>
