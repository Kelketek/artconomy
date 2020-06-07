<template>
  <v-container>
    <v-row dense>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-text>
            <h2>About {{username}}</h2>
            <v-row v-if="badges">
              <v-col>
                <v-chip :color="badge.color" v-for="badge in badges" :key="badge.label" class="mx-1" :light="badge.light">
                  <strong>{{badge.label}}</strong>
                </v-chip>
              </v-col>
            </v-row>
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

declare interface ProfileBadge {
  label: string,
  color: string,
  light: boolean
}

  @Component({
    components: {AcRendered, AcEditingToggle, AcPatchField, AcJournals},
  })
export default class AboutUser extends mixins(Subjective, Editable) {
  public get badges(): ProfileBadge[] {
    const badges: ProfileBadge[] = []
    if (!this.subjectHandler.artistProfile.x) {
      return badges
    }
    if (this.subjectHandler.artistProfile.x.lgbt) {
      badges.push({label: 'LGBTQ+', color: 'purple', light: false})
    }
    if (this.subjectHandler.artistProfile.x.artist_of_color) {
      badges.push({label: 'Artist of Color', color: 'orange', light: true})
    }
    return badges
  }
}
</script>
