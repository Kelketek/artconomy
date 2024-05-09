<template>
  <ac-load-section :controller="character.profile">
    <ac-subjective-toolbar :username="username">
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
                           v-if="controls"
                           :allow-multiple="true"
                           ref="submissionDialog"
                           @success="success"
        />
        <v-menu offset-x left v-if="controls" :close-on-content-click="false" :attach="$menuTarget">
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

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import AcConfirmation from '../../wrappers/AcConfirmation.vue'
import CharacterCentric from './mixins/CharacterCentric.ts'
import AcShareButton from '../../AcShareButton.vue'
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import AcRelatedManager from '../../wrappers/AcRelatedManager.vue'
import AcBoundField from '../../fields/AcBoundField.ts'
import AcAvatar from '../../AcAvatar.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import AcSubjectiveToolbar from '@/components/navigation/AcSubjectiveToolbar.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {Character} from '@/store/characters/types/Character.ts'
import {newUploadSchema} from '@/lib/lib.ts'
import Upload from '@/mixins/upload.ts'
import AcShareManager from '@/components/AcShareManager.vue'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Editable from '@/mixins/editable.ts'
import Sharable from '@/mixins/sharable.ts'
import Submission from '@/types/Submission.ts'
import {defineAsyncComponent} from 'vue'
import {mdiDelete, mdiPencil, mdiLock, mdiDotsHorizontal, mdiUpload} from '@mdi/js'
const AcNewSubmission = defineAsyncComponent(() => import('@/components/AcNewSubmission.vue'))

@Component({
  components: {
    AcLink,
    AcMiniCharacter,
    AcShareManager,
    AcNewSubmission,
    AcFormDialog,
    AcSubjectiveToolbar,
    AcAvatar,
    AcBoundField,
    AcRelatedManager,
    AcLoadSection,
    AcShareButton,
    AcConfirmation,
  },
  emits: ['success'],
})
class AcCharacterToolbar extends mixins(CharacterCentric, Upload, Editable, Sharable) {
  @Prop({default: true})
  public characterAvatar!: boolean

  @Prop({default: false})
  public showEdit!: boolean

  public newUpload: FormController = null as unknown as FormController
  public step = 1
  public mdiDelete = mdiDelete
  public mdiPencil = mdiPencil
  public mdiLock = mdiLock
  public mdiDotsHorizontal = mdiDotsHorizontal
  public mdiUpload = mdiUpload

  public success(submission: Submission) {
    this.showUpload = false
    this.$emit('success', submission)
  }

  public deleteCharacter() {
    return this.character.profile.delete().then(() => {
      return this.$router.replace({
        name: 'Profile',
        params: {username: this.username},
      })
    })
  }

  public get preloadedCharacter() {
    return [this.character.profile.x]
  }

  @Watch('character.profile.x', {
    deep: true,
    immediate: true,
  })
  public updateSubmissionTags(val: Character | null | undefined) {
    if (!val) {
      return
    }
    this.newUpload.fields.tags.model = val.tags
    if (this.newUpload.fields.characters.model.indexOf(val.id) === -1) {
      this.newUpload.fields.characters.model.push(val.id)
      this.newUpload.fields.characters.initialData = [val.id]
    }
  }

  public get shareMedia() {
    const character = this.character.profile.x as Character
    /* istanbul ignore if */
    if (!character) {
      return null
    }
    if (!character.primary_submission) {
      return null
    }
    return character.primary_submission
  }

  public created() {
    this.newUpload = this.$getForm('newUpload', newUploadSchema(this.subjectHandler.user))
  }
}

export default toNative(AcCharacterToolbar)
</script>
