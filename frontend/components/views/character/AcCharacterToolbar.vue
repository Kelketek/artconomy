<template>
  <ac-load-section :controller="character.profile">
    <ac-subjective-toolbar :username="username" v-if="character.profile.x">
      <template v-if="characterAvatar" v-slot:avatar>
        <ac-mini-character :show-name="false" :character="character.profile.x" class="ml-3" :alt="character.profile.x!.name"/>
        <v-toolbar-title>
          <ac-link :to="{name: 'Character', params: {username, characterName}}">{{characterName}}</ac-link>
        </v-toolbar-title>
      </template>
      <v-toolbar-items class="text-center text-md-right" v-if="character.profile.x">
        <ac-share-button :title="`${characterName} by ${username} - Artconomy`" :media-url="shareMediaUrl"
                         :clean="shareMediaClean">
          <template v-slot:title>Share {{characterName}}</template>
          <template v-slot:footer v-if="controls">
            <ac-load-section :controller="character.sharedWith">
              <ac-share-manager :controller="character.sharedWith"/>
            </ac-load-section>
          </template>
        </ac-share-button>
        <v-btn color="green" variant="flat" @click="showUpload = true" v-if="controls" class="upload-button">
          <v-icon left :icon="mdiUpload"/>
          Upload
        </v-btn>
        <ac-new-submission :show-characters="!!character.profile.x"
                           :character-init-items="preloadedCharacter"
                           v-model="showUpload"
                           :username="username"
                           :visit="visit"
                           v-if="controls && preloadedCharacter"
                           :allow-multiple="true"
                           ref="submissionDialog"
                           @success="success"
        />
        <v-menu offset-x left v-if="controls" :close-on-content-click="false" :attach="menuTarget">
          <template v-slot:activator="{props}">
            <v-btn icon v-bind="props" class="more-button" aria-label="Actions">
              <v-icon :icon="mdiDotsHorizontal"/>
            </v-btn>
          </template>
          <v-list dense>
            <v-list-item @click.stop="editing = !editing" v-if="showEdit">
              <template v-slot:prepend>
                <v-icon v-if="editing" :icon="mdiLock"/>
                <v-icon v-else :icon="mdiPencil"/>
              </template>
              <v-list-item-title v-if="editing">Lock</v-list-item-title>
              <v-list-item-title v-else>Edit</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-switch v-model="character.profile.patchers.private.model"
                          :hide-details="true"
                          color="primary"
                />
              </template>
              <v-list-item-title>
                Private
              </v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-switch v-model="character.profile.patchers.nsfw.model"
                          :hide-details="true"
                          color="primary"
                />
              </template>
              <v-list-item-title>
                NSFW
              </v-list-item-title>
            </v-list-item>
            <ac-confirmation :action="deleteCharacter">
              <template v-slot:default="confirmContext">
                <v-list-item v-on="confirmContext.on">
                  <template v-slot:prepend>
                    <v-icon class="delete-button" :icon="mdiDelete"/>
                  </template>
                  <v-list-item-title>Delete</v-list-item-title>
                </v-list-item>
              </template>
            </ac-confirmation>
          </v-list>
        </v-menu>
      </v-toolbar-items>
    </ac-subjective-toolbar>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcShareButton from '@/components/AcShareButton.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcSubjectiveToolbar from '@/components/navigation/AcSubjectiveToolbar.vue'
import {useUpload} from '@/mixins/upload.ts'
import AcShareManager from '@/components/AcShareManager.vue'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {computed, defineAsyncComponent, ref} from 'vue'
import {mdiDelete, mdiPencil, mdiLock, mdiDotsHorizontal, mdiUpload} from '@mdi/js'
import {useCharacter} from '@/store/characters/hooks.ts'
import {useRouter} from 'vue-router'
import {useSharable} from '@/mixins/sharable.ts'
import {useTargets} from '@/plugins/targets.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useEditable} from '@/mixins/editable.ts'
import type {CharacterProps, Submission} from '@/types/main'
const AcNewSubmission = defineAsyncComponent(() => import('@/components/AcNewSubmission.vue'))

const props = withDefaults(
    defineProps<{characterAvatar?: boolean, showEdit?: boolean, visit?: boolean} & CharacterProps>(),
    {characterAvatar: true, showEdit: false, visit: true},
)
const {controls} = useSubject({ props })
const {editing} = useEditable(controls)
const router = useRouter()
const character = useCharacter(props)
const preloadedCharacter = computed(() => (character.profile.x && [character.profile.x]) || [])
const emit = defineEmits<{'success': [Submission]}>()
const {showUpload} = useUpload()
const {menuTarget} = useTargets()
const submissionDialog = ref<typeof AcNewSubmission|null>(null)


const shareMedia = computed(() => {
  const profile = character.profile.x
  /* istanbul ignore if */
  if (!profile) {
    return null
  }
  if (!profile.primary_submission) {
    return null
  }
  return profile.primary_submission
})
const {shareMediaClean, shareMediaUrl} = useSharable(shareMedia)

const success = (submission: Submission) => {
  showUpload.value = false
  emit('success', submission)
}

const deleteCharacter = async () => {
  return character.profile.delete().then(() => {
    return router.replace({
      name: 'Profile',
      params: {username: props.username},
    })
  })
}

defineExpose({showUpload})
</script>
