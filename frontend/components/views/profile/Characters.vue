<template>
  <v-container fluid class="pa-0">
    <v-row class="d-none d-md-flex">
      <v-col class="text-right">
        <v-btn color="green" @click="showNew = true" v-if="controls"><v-icon left>add</v-icon>New Character</v-btn>
      </v-col>
    </v-row>
    <ac-paginated :list="characters">
      <v-col class="pa-1" lg="2" md="3" cols="6" v-for="character in characters.list" :key="character.x.id">
        <ac-character-preview :character="character.x" :key="character.key"></ac-character-preview>
      </v-col>
    </ac-paginated>
    <ac-form-dialog
            v-if="controls"
            v-model="showNew"
            v-bind="form.bind"
            title="New Character"
            @submit="form.submitThen(visitCharacter)"
    >
      <v-row no-gutters  >
        <v-col cols="12">
          <ac-bound-field :field="form.fields.name" hint="Enter the name of your character." label="Character Name">

          </ac-bound-field>
        </v-col>
        <v-col cols="12">
          <ac-bound-field :field="form.fields.private"
                          field-type="ac-checkbox"
                          :persistent-hint="true"
                          label="Private"
                          hint="If checked, this character will not appear in search listings and will only be visible to users you explicitly share them with."
          >
          </ac-bound-field>
        </v-col>
      </v-row>
    </ac-form-dialog>
    <ac-add-button v-model="showNew" v-if="controls">New Character</ac-add-button>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {ListController} from '@/store/lists/controller'
import {Character} from '@/store/characters/types/Character'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcAddButton from '@/components/AcAddButton.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import {flatten} from '@/lib/lib'

  @Component({components: {AcBoundField, AcFormDialog, AcAddButton, AcPaginated, AcCharacterPreview}})
export default class Characters extends mixins(Subjective) {
    public characters: ListController<Character> = null as unknown as ListController<Character>
    public form: FormController = null as unknown as FormController
    public showNew = false

    public get url() {
      return `/api/profiles/v1/account/${this.username}/characters/`
    }

    public visitCharacter(character: Character) {
      this.$router.push({
        name: 'Character',
        params: {username: this.username, characterName: character.name},
        query: {editing: 'true'},
      })
    }

    public created() {
      this.characters = this.$getList(`${flatten(this.username)}-characters`, {endpoint: this.url, keyProp: 'name'})
      this.form = this.$getForm(`${flatten(this.username)}-newCharacter`, {
        endpoint: this.url,
        fields: {
          name: {value: ''}, private: {value: false},
        },
      })
      this.characters.firstRun().then()
    }
}
</script>
