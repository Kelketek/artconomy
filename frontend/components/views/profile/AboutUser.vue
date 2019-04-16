<template>
  <v-container>
    <v-layout row wrap>
      <v-flex xs12 md8>
        <v-card>
          <v-card-text>
            <h2>About {{username}}</h2>
            <small><strong>Views:</strong> {{subject.hits}} <strong>Watchers: </strong>{{subject.watches}}</small>
            <ac-patch-field field-type="ac-editor" :patcher="subjectHandler.user.patchers.biography" v-show="editing"
                            :auto-save="false" v-if="controls"></ac-patch-field>
            <ac-rendered v-show="!editing" :value="subject.biography" :truncate="true"></ac-rendered>
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex xs12 md4>
        <ac-journals :username="username"></ac-journals>
      </v-flex>
    </v-layout>
    <ac-editing-toggle v-if="controls"></ac-editing-toggle>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcJournals from '@/components/AcJournals.vue'
import Subjective from '@/mixins/subjective'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcEditingToggle from '@/components/navigation/AcEditingToggle.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import {Patch} from '@/store/singles/patcher'
import Editable from '@/mixins/editable'
  @Component({
    components: {AcRendered, AcEditingToggle, AcPatchField, AcJournals},
  })
export default class AboutUser extends mixins(Subjective, Editable) {
}
</script>
