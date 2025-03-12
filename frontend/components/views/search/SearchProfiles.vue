<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-col
      v-for="user in list.list"
      :key="user.x!.id"
      cols="4"
      sm="3"
      md="2"
      lg="1"
    >
      <ac-avatar :user="user.x" />
    </v-col>
  </ac-paginated>
</template>
<script setup lang="ts">
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import AcAvatar from "@/components/AcAvatar.vue"
import { useList } from "@/store/lists/hooks.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { useSearchList } from "@/components/views/search/mixins/SearchList.ts"
import { TerseUser } from "@/store/profiles/types/main"

const list = useList<TerseUser>("searchProfiles", {
  endpoint: "/api/profiles/search/user/",
  persistent: true,
})
const searchForm = useForm("search")
useSearchList(searchForm, list)
</script>
