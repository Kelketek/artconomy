<template>
  <v-flex>
    <v-flex v-if="journals.ready">
      <v-toolbar dense color="secondary">
        <v-toolbar-title>Journals</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn color="green" @click="showNew = true" v-if="isCurrent"><v-icon left>add</v-icon>Add New</v-btn>
      </v-toolbar>
      <v-layout class="elevation-4">
        <v-layout column>
          <v-flex>
            <v-list two-line>
              <template v-for="item in journals.list">
                <v-list-tile
                    :key="item.x.id"
                    avatar
                    :to="{name: 'Journal', params: {username, journalId: item.x.id}}"
                >
                  <v-list-tile-avatar>
                    <v-icon>edit</v-icon>
                  </v-list-tile-avatar>
                  <v-list-tile-content>
                    <v-list-tile-title>{{item.x.subject}}</v-list-tile-title>
                    <v-list-tile-sub-title>{{formatDate(item.x.created_on)}}</v-list-tile-sub-title>
                  </v-list-tile-content>
                </v-list-tile>
              </template>
            </v-list>
          </v-flex>
        </v-layout>
      </v-layout>
    </v-flex>
    <ac-loading-spinner v-else></ac-loading-spinner>
    <ac-form-dialog
        v-model="showNew"
        v-if="isCurrent"
        v-bind="newJournal.bind"
        @submit="newJournal.submitThen(visitJournal)"
        :large="true"
    >
      <v-flex xs12 sm10 offset-sm1 offset-md2 md8>
        <ac-bound-field :field="newJournal.fields.subject" label="Subject" autofocus></ac-bound-field>
      </v-flex>
      <v-flex xs12 sm10 offset-sm1 offset-md2 md8 mt-2>
        <ac-bound-field :field="newJournal.fields.body" field-type="ac-editor" label="Body"
                        :auto-save="true" :save-indicator="false"
        ></ac-bound-field>
      </v-flex>
      <v-flex xs12 sm10 offset-sm1 offset-md2 md8>
        <ac-bound-field :field="newJournal.fields.comments_disabled" field-type="v-checkbox" :persistent-hint="true"
                        label="Comments Disabled"
                        hint="If checked, prevents people from commenting on this journal."
        ></ac-bound-field>
      </v-flex>
    </ac-form-dialog>
  </v-flex>
</template>

<script lang="ts">
// import Paginated from './mixins/paginated'
import Formatting from '@/mixins/formatting'
import {truncateText} from '@/lib'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {Journal} from '@/types/Journal'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import AcRendered from '@/components/wrappers/AcRendered'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'

  @Component({
    components: {AcGrowSpinner, AcLoadingSpinner, AcRendered, AcBoundField, AcFormDialog},
  })
export default class AcJournals extends mixins(Subjective, Formatting) {
    public firstRun: boolean = true
    public currentJournal: null|Journal = null
    public showNew = false
    public journals: ListController<Journal> = null as unknown as ListController<Journal>
    public newJournal: FormController = null as unknown as FormController

    public created() {
      this.newJournal = this.$getForm(this.username + '-newJournal', {
        endpoint: this.url,
        fields: {
          subject: {value: '', validators: [{name: 'required'}]},
          body: {value: '', validators: [{name: 'required'}]},
          comments_disabled: {value: false},
        },
      })
      this.journals = this.$getList(this.username + '-journals', {endpoint: this.url, pageSize: 3, grow: true})
      this.journals.firstRun().then()
    }

    public visitJournal(response: Journal) {
      this.$router.push({name: 'Journal', params: {username: this.username, journalId: response.id + ''}})
    }

    public get url() {
      return `/api/profiles/v1/account/${this.username}/journals/`
    }

    public get preview() {
      if (!this.currentJournal) {
        return ''
      }
      return truncateText(this.currentJournal.body, 1000)
    }
}
</script>
