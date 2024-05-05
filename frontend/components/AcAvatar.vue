<template>
  <div class="ac-avatar shrink text-center flex">
    <div class="flex">
      <div class="flex">
        <ac-link :to="profileLink">
          <v-avatar :aria-label="`Profile for ${displayName}`">
            <img alt="" :src="person.avatar_url" v-if="person" width="40" height="40">
            <v-icon v-else :icon="mdiAccount"/>
          </v-avatar>
        </ac-link>
      </div>
      <div v-if="showName" class="text-center flex">
        <v-tooltip bottom v-if="person && person.is_superuser" aria-label="Admin status tooltip">
          <template v-slot:activator="{props}">
            <v-icon size="small" color="green" v-bind="props" :icon="mdiStarCircle"/>
          </template>
          <span>Admin</span>
        </v-tooltip>
        <v-tooltip bottom v-else-if="person && person.is_staff" aria-label="Staff status tooltip">
          <template v-slot:activator="{props}">
            <v-icon v-bind="props" size="small" color="yellow" :icon="mdiStarCircle"/>
          </template>
          <span>Staff</span>
        </v-tooltip>
        <ac-link :to="profileLink">{{ displayName }}</ac-link>
      </div>
      <div v-if="person && removable" class="flex">
        <v-btn size="x-small" icon color="danger" @click="emit('remove')">
          <v-icon size="large" :icon="mdiClose"/>
        </v-btn>
      </div>
      <router-link :to="{name: 'Ratings', params: {username: person.username}}"
                   v-if="showRating && person && person.stars">
        <v-rating density="compact" size="small" half-increments :model-value="starRound(person.stars)" color="primary"/>
      </router-link>
    </div>
  </div>
</template>

<style>
/*noinspection CssUnusedSymbol*/
.ac-avatar .v-rating.v-rating--dense .v-icon {
  padding: 0.025rem;
}
</style>

<script setup lang="ts">
import {ProfileController} from '@/store/profiles/controller.ts'
import {User} from '@/store/profiles/types/User.ts'
import {artCall, starRound, useForceRecompute} from '@/lib/lib.ts'
import {profileRegistry} from '@/store/profiles/registry.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import {mdiAccount, mdiClose, mdiStarCircle} from '@mdi/js'
import {profileLink as getProfileLink} from '@/lib/otherFormatters.ts'
import {computed, watch, onUnmounted} from 'vue'
import {ArtState} from '@/store/artState.ts'
import {useStore} from 'vuex'
import {getUid, useRegistries} from '@/store/hooks.ts'
import {getController, performUnhook} from '@/store/registry-base.ts'
import {useSocket} from '@/plugins/socket.ts'
import {useRouter} from 'vue-router'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts.ts'
import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'

// The logic for this module is a bit complex because we don't necessarily want to store the user in Vuex for
// all the cases we'll use this. For example, when searching for users, it would be wasteful or incomplete to
// store the user in Vuex.
export interface AcAvatarProps {
  noLink?: boolean,
  username?: string,
  user?: null|TerseUser|User|RelatedUser,
  userId?: number,
  showName?: boolean,
  showRating?: boolean,
  removable?: boolean,
  inline?: boolean,
}

const props = withDefaults(
    defineProps<AcAvatarProps>(),
    {
      noLink: false,
      username: '',
      showName: true,
      showRating: false,
      removable: false,
      inline: false,
    },
)

const emit = defineEmits<{remove: []}>()

const store = useStore<ArtState>()

let subjectHandler: ProfileController|undefined = undefined
const {check, recalculate} = useForceRecompute()

const setUser = (response: User) => {
  subjectHandler = useProfile(response.username)
  subjectHandler.user.setX(response)
  recalculate()
}

const buildHandler = (username: string) => {
  if (username) {
    subjectHandler = useProfile(username)
    subjectHandler.user.get().then().catch(() => {})
    recalculate()
    return
  }
  if (!props.userId) {
    console.error('No username, no ID. We cannot load an avatar.')
    return
  }
  if (store.getters.idMap[props.userId]) {
    username = store.getters.idMap[props.userId]
    subjectHandler = useProfile(username)
    recalculate()
  } else {
    artCall({
      url: `/api/profiles/data/user/id/${props.userId}/`,
      method: 'get',
    }).then(setUser).catch(() => {})
  }
}

const subject = computed(() => {
  check()
  return subjectHandler?.user.x as TerseUser
})

const person = computed(() => {
  return props.user || subject.value || null
})

const uid = getUid()
const socket = useSocket()
const router = useRouter()
const registries = useRegistries()

// Custom version of useProfile since we have to fetch it out of band.
const useProfile = (username: string) => {
  return getController<ProfileState, ProfileModuleOpts, ProfileController>({
    name: username,
    schema: {},
    uid,
    socket,
    typeName: 'Profile',
    store,
    router,
    registries,
    ControllerClass: ProfileController,
})}

// Due to the custom mounting, we have to do the custom unmounting as well.
onUnmounted(() => performUnhook<ProfileState, ProfileModuleOpts, ProfileController>(uid, registries['Profile']))


watch(() => props.username, (value: string) => {
  if (!value) {
    // Can happen on destruction
    return
  }
  if (!subjectHandler) {
    return
  }
  profileRegistry.unhook(uid, subjectHandler)
  buildHandler(value)
})

const displayName = computed(() => {
  if (person.value) {
    return person.value.username
  }
  if (props.username) {
    return props.username
  }
  if (props.userId) {
    return `(User ID #${props.userId})`
  }
  return '(Loading)'
})

const profileLink = computed(() => {
  if (props.noLink) {
    return null
  }
  return getProfileLink(person.value)
})

if (!props.user) {
  buildHandler(props.username)
}
</script>
