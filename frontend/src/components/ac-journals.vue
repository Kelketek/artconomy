<template>
  <v-card v-if="response">
    <v-card-title><h2>Journals</h2></v-card-title>
    <v-card-text>
      <v-layout row wrap>
        <v-flex xs12 md8>
          <v-layout row wrap>
            <v-flex xs12 v-if="currentJournal">
              <h3 v-html="md.renderInline(currentJournal.subject)"></h3>
              <v-flex v-html="md.render(preview)" my-2></v-flex>
            </v-flex>
            <v-flex xs12 v-if="currentJournal">
              <v-btn
                  color="purple"
                  v-if="currentJournal"
                  :to="{name: 'Journal', params: {username: username, journalID: currentJournal.id}}"
              >
                Read more/comment
              </v-btn>
            </v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs12 md4 pl-2>
          <v-layout row wrap>
            <v-flex xs12>
              <v-list two-line>
                <template v-for="(item, index) in growing">
                  <v-list-tile
                      :key="item.subject"
                      avatar
                      @click="currentJournal = item"
                  >
                    <v-list-tile-avatar>
                      <v-icon v-if="currentJournal && currentJournal.id === item.id">mail</v-icon>
                      <v-icon v-else>mail_outline</v-icon>
                    </v-list-tile-avatar>
                    <v-list-tile-content>
                      <v-list-tile-title>{{item.subject}}</v-list-tile-title>
                      <v-list-tile-sub-title>{{formatDateTime(item.created_on)}}</v-list-tile-sub-title>
                    </v-list-tile-content>
                  </v-list-tile>
                </template>
              </v-list>
            </v-flex>
            <v-flex xs12 text-xs-center>
              <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
            </v-flex>
            <v-flex xs12 v-if="isCurrent" text-xs-center>
              <v-btn color="primary" @click="showNew = true">Add New</v-btn>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
    </v-card-text>
    <ac-form-dialog ref="newJournalForm" :schema="newJournalSchema" :model="newJournalModel"
                    :options="newJournalOptions" :success="addJournal"
                    v-model="showNew"
                    :url="`/api/profiles/v1/account/${user.username}/journals/`"
                    v-if="isCurrent"
    />
  </v-card>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormDialog from './ac-form-dialog'
  import {formatDateTime, md, truncateText} from '../lib'

  export default {
    name: 'ac-journals',
    components: {AcFormDialog},
    mixins: [Paginated, Viewer, Perms],
    methods: {
      addJournal (response) {
        this.$router.history.push({name: 'Journal', params: {username: this.username, journalID: response.id}})
      }
    },
    data () {
      return {
        url: `/api/profiles/v1/account/${this.username}/journals/`,
        firstRun: true,
        currentJournal: null,
        showNew: false,
        md,
        formatDateTime,
        newJournalModel: {
          subject: '',
          body: '',
          comments_disabled: false
        },
        newJournalSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Subject',
            model: 'subject',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-text',
            label: 'Body',
            model: 'body',
            featured: true,
            multiLine: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Disable Comments',
            model: 'is_artist',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If checked, viewers will not be able to comment on this journal.'
          }]
        },
        newJournalOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    computed: {
      preview () {
        return truncateText(this.currentJournal.body, 1000)
      }
    },
    watch: {
      response () {
        if (!this.firstRun) {
          return
        }
        this.currentJournal = this.growing[0]
        this.firstRun = false
      }
    },
    created () {
      this.fetchItems()
    }
  }
</script>