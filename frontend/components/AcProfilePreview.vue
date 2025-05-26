<template>
  <v-card class="profile-card">
    <ac-link :to="profileLink(user)">
      <v-img
        :src="user.avatar_url"
        :aspect-ratio="1"
        :allow-preview="false"
        :alt="`User avatar for ${user.username}`"
      />
    </ac-link>
    <v-card-title>
      <ac-link :to="profileLink(user)">
        {{ user.username }}
      </ac-link>
    </v-card-title>
  </v-card>
</template>

<script setup lang="ts">
import AcLink from "@/components/wrappers/AcLink.vue"
import { profileLink } from "@/lib/otherFormatters.ts"
import { User, TerseUser } from "@/store/profiles/types/main"

defineProps<{ user: User | TerseUser }>()
</script>
