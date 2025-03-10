<!--suppress JSUnusedLocalSymbols -->
<template>
  <ac-load-section :controller="subjectHandler.user">
    <v-navigation-drawer
      v-model="drawer"
      temporary
      right
      absolute
      width="300"
    >
      <v-list>
        <ac-setting-nav :username="username" />
      </v-list>
    </v-navigation-drawer>
    <v-container>
      <v-toolbar
        v-if="!isCurrent"
        color="red"
        class="settings-nav-toolbar"
      >
        <v-toolbar-title>
          Settings for
          <ac-link :to="profileLink(subject)">
            {{ username }}
          </ac-link>
        </v-toolbar-title>
        <v-spacer />
        <ac-avatar
          :username="username"
          :show-name="false"
        />
      </v-toolbar>
      <v-toolbar
        color="secondary"
        class="settings-nav-toolbar"
      >
        <v-toolbar-title>{{ route.name }}</v-toolbar-title>
        <v-spacer />
        <v-toolbar-items>
          <v-btn
            id="more-settings-button"
            color="primary"
            variant="flat"
            @click="drawer=true"
          >
            More Settings...
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <router-view />
    </v-container>
  </ac-load-section>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {profileLink} from '@/lib/otherFormatters.ts'
import type {SubjectiveProps} from '@/types/main'

const props = defineProps<SubjectiveProps>()

const {subjectHandler, subject, isCurrent} = useSubject({ props })

const drawer = ref(false)

const route = useRoute()
const router = useRouter()

onMounted(() => {
   if (route.name === 'Settings') {
     router.replace({name: 'Options', params: {username: props.username}})
   }
})
</script>
