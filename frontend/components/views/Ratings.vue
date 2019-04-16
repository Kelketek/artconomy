<template>
  <ac-load-section :controller="ratings">
    <v-container>
      <ac-profile-header :username="username"></ac-profile-header>
      <ac-paginated :list="ratings">
        <template v-slot:default>
          <v-layout row wrap>
            <v-flex v-for="rating in ratings.list" :key="rating.x.id" class="pb-2" xs12>
              <v-card>
                <v-card-text>
                  <v-layout row wrap>
                    <v-flex xs12 sm2 md1 text-xs-center text-sm-left>
                      <ac-avatar :user="rating.x.rater"></ac-avatar>
                    </v-flex>
                    <v-flex xs12 sm4 md2 text-xs-center text-sm-left>
                      <v-rating :readonly="true" dense :value="rating.x.stars"></v-rating>
                    </v-flex>
                    <v-flex xs12 sm6 md9 text-xs-center text-sm-left v-if="rating.x.comments">
                      <ac-rendered :value="rating.x.comments" />
                    </v-flex>
                  </v-layout>
                </v-card-text>
              </v-card>
            </v-flex>
          </v-layout>
        </template>
      </ac-paginated>
    </v-container>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {ListController} from '@/store/lists/controller'
import Subjective from '@/mixins/subjective'
import Rating from '@/types/Rating'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
  @Component({
    components: {AcProfileHeader, AcRendered, AcAvatar, AcPaginated, AcLoadSection},
  })
export default class Ratings extends mixins(Subjective) {
    public ratings: ListController<Rating> = null as unknown as ListController<Rating>

    public created() {
      this.ratings = this.$getList(
        `ratings__${this.username}`, {endpoint: `/api/sales/v1/account/${this.username}/ratings/`}
      )
      this.ratings.firstRun()
    }
}
</script>
