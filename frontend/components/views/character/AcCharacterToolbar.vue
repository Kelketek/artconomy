<template>
  <ac-load-section :controller="character.profile">
    <ac-subjective-toolbar :username="username">
      <template v-if="characterAvatar" v-slot:avatar>
        <ac-mini-character :show-name="false" :character="character.profile.x" />
        <v-toolbar-title><ac-link :to="{name: 'Character', params: {username, characterName}}">{{characterName}}</ac-link></v-toolbar-title>
      </template>
      <v-toolbar-items class="text-center text-md-right" v-if="character.profile.x">
        <ac-share-button :title="`${characterName} by ${username} - Artconomy`" :media-url="shareMediaUrl" :clean="shareMediaClean">
          <span slot="title">Share {{characterName}}</span>
          <template v-slot:footer v-if="controls">
            <ac-load-section :controller="character.sharedWith">
              <ac-share-manager :controller="character.sharedWith" />
            </ac-load-section>
          </template>
        </ac-share-button>
        <v-btn color="green" @click="showUpload = true" v-if="controls"><v-icon left>fa-upload</v-icon> Upload</v-btn>
        <ac-new-submission :show-characters="character.profile.x" :character-init-items="preloadedCharacter"
                           v-model="showUpload"
                           :username="username"
                           v-if="controls"
        />
        <v-menu offset-x left v-if="controls" :close-on-content-click="false">
          <template v-slot:activator="{on}">
            <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
          </template>
          <v-list dense>
            <v-list-item @click.stop="editing = !editing" v-if="showEdit">
              <v-list-item-action>
                <v-icon v-if="editing">lock</v-icon>
                <v-icon v-else>edit</v-icon>
              </v-list-item-action>
              <v-list-item-title v-if="editing">Lock</v-list-item-title>
              <v-list-item-title v-else>Edit</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-action>
                <v-switch v-model="character.profile.patchers.private.model"
                          :hide-details="true"
                />
              </v-list-item-action>
              <v-list-item-title>
                Private
              </v-list-item-title>
            </v-list-item>
            <ac-confirmation :action="deleteCharacter">
              <template v-slot:default="confirmContext">
                <v-list-item v-on="confirmContext.on">
                  <v-list-item-action class="delete-button"><v-icon>delete</v-icon></v-list-item-action>
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
import Component, {mixins} from 'vue-class-component'
import AcConfirmation from '../../wrappers/AcConfirmation.vue'
import CharacterCentric from './mixins/CharacterCentric'
import AcShareButton from '../../AcShareButton.vue'
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import AcRelatedManager from '../../wrappers/AcRelatedManager.vue'
import AcBoundField from '../../fields/AcBoundField'
import AcAvatar from '../../AcAvatar.vue'
import {FormController} from '@/store/forms/form-controller'
import {Fragment} from 'vue-fragment'
import AcSubjectiveToolbar from '@/components/navigation/AcSubjectiveToolbar.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {Prop, Watch} from 'vue-property-decorator'
import {Character} from '@/store/characters/types/Character'
import {newUploadSchema} from '@/lib/lib'
import Upload from '@/mixins/upload'
import AcNewSubmission from '@/components/AcNewSubmission.vue'
import AcShareManager from '@/components/AcShareManager.vue'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Editable from '@/mixins/editable'
import Sharable from '@/mixins/sharable'

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
    Fragment,
  },
})
export default class AcCharacterToolbar extends mixins(CharacterCentric, Upload, Editable, Sharable) {
    @Prop({default: true})
    public characterAvatar!: boolean

    @Prop({default: false})
    public showEdit!: boolean

    public newShare: FormController = null as unknown as FormController
    public newUpload: FormController = null as unknown as FormController
    public step = 1

    public deleteCharacter() {
      this.character.profile.delete().then(() => {
        this.$router.replace({name: 'Profile', params: {username: this.username}})
      })
    }

    public get preloadedCharacter() {
      return [this.character.profile.x]
    }

    @Watch('character.profile.x', {deep: true, immediate: true})
    public updateSubmissionTags(val: Character|null|undefined) {
      if (!val) {
        return
      }
      this.newUpload.fields.tags.model = val.tags
      if (this.newUpload.fields.characters.model.indexOf(val.id) === -1) {
        this.newUpload.fields.characters.model.push(val.id)
      }
    }

    public get shareMedia() {
      const character = this.character.profile.x as Character
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
</script>
