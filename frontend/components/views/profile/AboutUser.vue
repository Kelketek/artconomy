<template>
  <v-container>
    <v-row dense>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-text>
            <h2>About {{username}}</h2>
            <small><strong>Views:</strong> {{subject.hits}} <strong>Watchers: </strong>{{subject.watches}}</small>
            <ac-patch-field field-type="ac-editor" :patcher="subjectHandler.user.patchers.biography" v-show="editing"
                            :auto-save="false" v-if="controls" />
            <ac-rendered v-show="!editing" :value="subject.biography" :truncate="true" />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <ac-journals :username="username" />
      </v-col>
    </v-row>
    <ac-editing-toggle v-if="controls" />
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcJournals from '@/components/AcJournals.vue'
import Subjective from '@/mixins/subjective'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcEditingToggle from '@/components/navigation/AcEditingToggle.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import Editable from '@/mixins/editable'
  @Component({
    components: {AcRendered, AcEditingToggle, AcPatchField, AcJournals},
  })
export default class AboutUser extends mixins(Subjective, Editable) {
}
</script>
