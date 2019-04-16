<template>
  <v-container>
    <ac-character-toolbar :username="username" :character-name="characterName" :character-avatar="false"></ac-character-toolbar>
    <ac-load-section :controller="character.profile" tag="v-layout" class="mt-3">
      <template v-slot:default>
        <v-card class="mb-2">
          <v-card-text>
            <v-layout row wrap>
              <v-flex xs12 sm8 md7 lg8 xl9>
                <v-card-title primary-title>
                  <h1 v-show="!editing">{{character.profile.x.name}}</h1>
                  <ac-patch-field
                      :patcher="character.profile.patchers.name" :persistant-hint="true"
                      v-show="editing"
                      v-if="controls"
                      :auto-save="false"
                      :enter-save="true"
                      label="Name"
                      hint="WARNING: Changing this character's name will change the URL of the
                  character, which can affect SEO."
                  ></ac-patch-field>
                </v-card-title>
                <ac-attributes :username="username" :character-name="characterName"></ac-attributes>
                <ac-tag-display
                    :patcher="character.profile.patchers.tags" :editable="character.profile.x.taggable" :username="username"
                    scope="Characters"
                ></ac-tag-display>
              </v-flex>
              <v-flex xs12 sm4 md4 lg3 xl2 offset-md1>
                <v-layout align-content-center align-center justify-center row>
                  <v-flex align-self-center>
                    <ac-link :to="primarySubmissionLink">
                      <ac-asset :asset="character.profile.x.primary_submission"
                                thumb-name="thumbnail" :terse="true"
                                :editing="editing"
                                v-model="showChangePrimary"
                      >
                        <template slot="edit-menu">
                          <ac-expanded-property v-model="showChangePrimary" :large="true">
                            <span slot="title">Change Showcase Submission</span>
                            <ac-patch-field
                                field-type="ac-submission-select"
                                :patcher="character.profile.patchers.primary_submission"
                                :query-endpoint="character.submissions.endpoint"
                                :save-comparison="character.profile.x.primary_submission"
                                :show-progress="true"
                            >
                            </ac-patch-field>
                            <template v-slot:actions>
                              <v-spacer></v-spacer>
                              <v-btn color="danger" v-if="character.profile.x.primary_submission" @click="character.profile.patch({primary_submission: null})">Clear Showcased Image</v-btn>
                              <v-btn color="primary" @click="showChangePrimary = false">Cancel</v-btn>
                            </template>
                          </ac-expanded-property>
                        </template>
                      </ac-asset>
                    </ac-link>
                  </v-flex>
                </v-layout>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
        <v-card>
          <v-card-text>
            <v-card-title primary-title><h2>About {{character.profile.x.name}}</h2></v-card-title>
            <ac-patch-field
                field-type="ac-editor"
                :auto-save="false"
                :patcher="character.profile.patchers.description"
                v-if="controls"
                v-show="editing"
                :save-comparison="character.profile.patchers.description.rawValue" />
            <ac-rendered :value="character.profile.patchers.description.rawValue" v-show="!editing"></ac-rendered>
          </v-card-text>
        </v-card>
        <ac-colors :username="username" :character-name="characterName"></ac-colors>
        <v-card v-if="editing || character.profile.x.open_requests" class="mt-3">
          <v-card-text>
            <v-layout row wrap class="mb-2">
              <ac-patch-field field-type="v-checkbox"
                              hint="If this is checked, permits others to commission art involving your characters."
                              label="Open Requests"
                              :persistent-hint="true"
                              v-if="controls"
                              v-show="editing"
                              :save-indicator="false"
                              :patcher="character.profile.patchers.open_requests"
              >
              </ac-patch-field>
              <v-flex xs12 v-if="character.profile.x.open_requests" v-show="!editing">
                <h3><v-icon left color="green">check_circle</v-icon> Character can be used in other people's commissions</h3>
              </v-flex>
            </v-layout>
            <v-layout row wrap>
              <ac-patch-field
                  field-type="ac-editor"
                  :auto-save="false"
                  :patcher="character.profile.patchers.open_requests_restrictions"
                  v-if="controls"
                  v-show="editing"
                  label="Restrictions"
                  hint="Write any restrictions you wish to place on having your character commissioned by others.
                  For instance, if your character would never eat pie, you could write, 'Don't draw them eating pie.'"
                  :disabled="!character.profile.patchers.open_requests.model"
                  :save-comparison="character.profile.x.open_requests_restrictions" />
              <v-flex xs12 v-if="character.profile.x.open_requests_restrictions" v-show="!editing">
                <h4 class="mb-2"><v-icon color="yellow" left>warning</v-icon>With the following restrictions:</h4>
                <ac-rendered :value="character.profile.x.open_requests_restrictions"></ac-rendered>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
        <ac-context-gallery
            class="mt-3"
            :username="username" :character-name="characterName"
        />
        <ac-editing-toggle v-if="controls"></ac-editing-toggle>
      </template>
    </ac-load-section>
  </v-container>
</template>

<script lang="ts">
import AcAsset from '@/components/AcAsset.vue'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {Character} from '@/store/characters/types/Character'
import AcAvatar from '@/components/AcAvatar.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher'
import AcRendered from '@/components/wrappers/AcRendered'
import Editable from '@/mixins/editable'
import AcEditingToggle from '@/components/navigation/AcEditingToggle.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import CharacterCentric from '@/components/views/character/mixins/CharacterCentric'
import AcAttributes from '@/components/views/character/AcAttributes.vue'
import AcColors from '@/components/views/character/AcColors.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import AcContextGallery from '@/components/views/character/AcContextGallery.vue'
import Submission from '@/types/Submission'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcShareButton from '@/components/AcShareButton.vue'
import {FormController} from '@/store/forms/form-controller'
import AcRelatedManager from '@/components/wrappers/AcRelatedManager.vue'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import {Watch} from 'vue-property-decorator'
import {setMetaContent, textualize} from '@/lib'

  @Component({components: {
    AcExpandedProperty,
    AcCharacterToolbar,
    AcRelatedManager,
    AcShareButton,
    AcLink,
    AcContextGallery,
    AcTagDisplay,
    AcColors,
    AcAttributes,
    AcConfirmation,
    AcBoundField,
    AcFormContainer,
    AcLoadSection,
    AcEditingToggle,
    AcRendered,
    AcPatchField,
    AcAvatar,
    AcAsset}})
export default class CharacterDetail extends mixins(Subjective, CharacterCentric, Editable) {
    public newShare: FormController = null as unknown as FormController
    public name: Patch = null as unknown as Patch
    public showChangePrimary = false

    public get primarySubmissionLink() {
      if (this.editing) {
        return null
      }
      const character = this.character.profile.x as Character
      if (!character.primary_submission) {
        return null
      }
      return {name: 'Submission', params: {submissionId: character.primary_submission.id}}
    }

    @Watch('character.profile.x.primary_submission.id')
    public closeSubmissionDialog() {
      this.showChangePrimary = false
    }

    @Watch('character.profile.x', {deep: true, immediate: true})
    public setMeta(character: Character|null) {
      // istanbul ignore if
      if (!character) {
        return
      }
      document.title = `${character.name} - ${character.user.username} on Artconomy.com`
      setMetaContent('description', textualize(character.description).slice(0, 160))
    }

    public created() {
      this.newShare = this.$getForm('share_character', {
        endpoint: this.character.sharedWith.endpoint,
        fields: {user_id: {value: null}},
      })
      this.character.profile.get().catch(this.setError)
      this.character.attributes.firstRun().then()
      this.character.colors.firstRun().then()
      this.character.sharedWith.firstRun().then()
    }
}
</script>